import uuid
from asyncio import Event
from decimal import Decimal
from django.utils.timezone import is_naive, make_aware
import pytz
from django.utils.timezone import make_aware, now
from datetime import datetime, time
from django.conf import settings
from django.contrib import messages
from django.utils.timezone import make_aware, now
import re

from django.db.models import Q, F
from django.contrib.auth.mixins import LoginRequiredMixin
from collections import defaultdict
from calendar import monthrange
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render, get_object_or_404, redirect
from datetime import date
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.core.exceptions import ObjectDoesNotExist
import json

from yookassa import Payment

from admin_settings.models import WorkingDay, Holiday, Table, Equipment
from management.models import SpecialOffer, PromoCode, PromoCodeUsage, MaxUnpaidBookings
from events.forms import BookingForm
from management.LoyaltyEngine import LoyaltyEngine
from pricing.models import PricingPlan
from .BookingEngine import BookingEngine
from .models import Booking, BookingEquipment, TableTypePricing


def booking_view(request):
    view_type = request.GET.get('view', 'day')
    selected_date_str = request.GET.get('current_date') or request.GET.get('date')
    selected_date = date.fromisoformat(selected_date_str) if selected_date_str else date.today()
    table_filter = request.GET.get('table', 'all')
    status_filter = request.GET.get('status', 'all')

    tables = Table.objects.filter(is_active=True).order_by('number')
    if table_filter != 'all':
        tables = tables.filter(id=table_filter)

    # Получаем активный тарифный план
    today = date.today()
    pricing_plan = PricingPlan.objects.filter(
        valid_from__lte=today,
        valid_to__gte=today
    ).first() or PricingPlan.objects.filter(is_default=True).first()

    context = {
        'tables': tables,
        'cols_class': f"grid-cols-{len(tables)}",
        'current_date': selected_date,
        'view_type': view_type,
        'table_filter': table_filter,
        'status_filter': status_filter,
        'pricing_plan': pricing_plan,
    }
    return render(request, "bookings/bookings.html", context)


class CalendarAPIView(APIView):
    permission_classes = [AllowAny]  # Доступ для всех, в том числе анонимных

    def get(self, request, *args, **kwargs):
        view_type = request.query_params.get('view', 'day')
        date_str = request.query_params.get('date')
        user = request.user if request.user.is_authenticated else None

        if not date_str:
            return Response({"error": "Parameter 'date' is required."}, status=400)

        date = parse_date(date_str)
        if date is None:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        user = request.user if request.user.is_authenticated else None

        # Получаем slot_view_mode: из пользователя, если есть, иначе из query params, иначе 60
        slot_view_mode_param = request.query_params.get('slot_view_mode')
        if slot_view_mode_param:
            try:
                slot_duration = int(slot_view_mode_param)
                if slot_duration <= 0:
                    slot_duration = 60
            except ValueError:
                slot_duration = 60
        else:
            slot_duration = getattr(user, 'slot_view_mode', 60) if user else 60
            if not slot_duration or slot_duration <= 0:
                slot_duration = 60

        if view_type == 'day':
            return self.get_day_view(date, user, slot_duration)
        elif view_type == 'week':
            return self.get_week_view(date, user, slot_duration)
        elif view_type == 'month':
            return self.get_month_view(date, user, slot_duration)
        else:
            return Response({"error": "Invalid view type. Must be 'day', 'week', or 'month'."}, status=400)

    def get_open_close_times(self, date):
        holiday = Holiday.objects.filter(date=date).first()
        if holiday:
            if holiday.status == 'closed':
                return False, None, None, False
            shortened = (holiday.status == 'shortened')
            return True, holiday.open_time, holiday.close_time, shortened

        weekday = date.weekday()
        wd = WorkingDay.objects.filter(day=weekday, is_open=True).first()
        if wd:
            return True, wd.open_time, wd.close_time, False

        return False, None, None, False

    def get_bookings(self, start, end, user):
        # Для админа возвращаем все бронирования
        if user and user.is_staff:
            return Booking.objects.filter(
                start_time__lt=end,
                end_time__gt=start
            )

        # Для обычных пользователей возвращаем только их бронирования
        if user:
            return Booking.objects.filter(
                start_time__lt=end,
                end_time__gt=start,

            )

        # Для анонимных пользователей не возвращаем бронирования
        return Booking.objects.none()
    def get_day_view(self, date, user, slot_duration):

        is_working_day, open_time, close_time, shortened = self.get_open_close_times(date)
        if not is_working_day:
            return Response({
                "date": date.strftime('%Y-%m-%d'),
                "is_working_day": False,
                "shortened": False,
                "working_hours": None,
                'weekday': date.weekday(),
                "tables": [],
                "time_slots": [],
                "day_schedule": {}
            })

        tz = pytz.timezone('Europe/Moscow')
        now = timezone.now().astimezone(tz)

        # Создание start_dt и end_dt как aware сразу
        start_dt = tz.localize(datetime.combine(date, open_time))
        end_dt = tz.localize(datetime.combine(date, close_time))

        # Пользовательские бронирования
        if user:
            today = now.astimezone(tz).date()
            start_of_today = tz.localize(datetime.combine(today, time.min))

            user_bookings_qs = Booking.objects.filter(
                user=user,
                start_time__gte=start_of_today
            )

            user_bookings = [{
                'id': b.id,
                'date': b.start_time.date().isoformat(),
                'start': b.start_time.strftime('%H:%M'),
                'end': b.end_time.strftime('%H:%M'),
                'table_number': b.table.number if b.table else None,
                'table_type': str(b.table.table_type) if b.table and b.table.table_type else None,
                'status': b.get_status_display()
            } for b in user_bookings_qs]
        else:
            user_bookings = []

        tables = Table.objects.filter(is_active=True).order_by('number')

        # Генерация временных слотов
        slots = []
        current = start_dt
        if start_dt.minute != 0:
            next_hour = (start_dt + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            if next_hour > end_dt:
                next_hour = end_dt
            slots.append((current, next_hour))
            current = next_hour

        while current < end_dt:
            slot_end = current + timedelta(minutes=slot_duration)
            if slot_end > end_dt:
                slots.append((current, end_dt))
                break
            slots.append((current, slot_end))
            current = slot_end

        if current < end_dt and current + timedelta(minutes=slot_duration) == end_dt:
            slots.append((current, end_dt))

        bookings = self.get_bookings(start_dt, end_dt, user)
        booking_map = defaultdict(list)
        for b in bookings:
            booking_map[b.table_id].append((b.start_time, b.end_time, b.status))

        pricing_data = TableTypePricing.objects.select_related('pricing_plan', 'table_type')
        offers = SpecialOffer.objects.filter(is_active=True, valid_from__lte=date, valid_to__gte=date).prefetch_related(
            'tables')

        offers_by_table = defaultdict(list)
        for offer in offers:
            target_tables = tables if offer.apply_to_all else offer.tables.all()
            for table in target_tables:
                offers_by_table[table.id].append(offer)

        time_slots = []
        day_schedule = defaultdict(dict)
        print("now:", now)  # для дебага
        print("first_slot_start:", slots[0][0])
        print("first_slot_end:", slots[0][1])
        for slot_start, slot_end in slots:
            label = slot_start.strftime('%H:%M')
            slot_visible = False  # флаг


            for table in tables:
                overlapping_booking = next(
                    ((s, e, status) for s, e, status in booking_map.get(table.id, []) if
                     s < slot_end and e > slot_start),
                    None
                )

                is_past = slot_end <= now

                if is_past and not (user and user.is_staff):
                    continue  # Пропустить слот

                if overlapping_booking:
                    slot_status = overlapping_booking[2]  # берём статус из модели Booking
                elif is_past:
                    slot_status = '-'
                else:
                    slot_status = 'available'


                pricing = None
                for p in pricing_data:
                    if p.table_type != table.table_type:
                        continue
                    plan = p.pricing_plan
                    if plan.weekdays and str(slot_start.isoweekday()) not in plan.weekdays:
                        continue
                    if plan.time_from and plan.time_to:
                        if not (plan.time_from <= slot_start.time() < plan.time_to):
                            continue
                    pricing = p
                    break

                duration_hours = (slot_end - slot_start).total_seconds() / 3600
                base_price = pricing.hour_rate * duration_hours if pricing else 0
                discount = 0
                for offer in offers_by_table.get(table.id, []):
                    if str(slot_start.isoweekday()) in offer.weekdays:
                        if not offer.time_from or not offer.time_to or (
                                offer.time_from <= slot_start.time() < offer.time_to):
                            discount = max(discount, offer.discount_percent)

                final_price = base_price * (1 - discount / 100)

                day_schedule[table.id][label] = {
                    'status': slot_status,
                    'start': slot_start.strftime('%H:%M'),
                    'end': slot_end.strftime('%H:%M'),
                    'price': int(final_price),
                    'discount_applied': discount > 0,
                    'discount_percent': discount,
                    'slot_duration': slot_duration
                }

                slot_visible = True  # хотя бы один слот видим

            if slot_visible:
                time_slots.append(label)
        return Response({
            'date': date.strftime('%Y-%m-%d'),
            'is_working_day': True,
            'shortened': shortened,
            'weekday': date.weekday(),
            'slot_duration': slot_duration,
            'working_hours': {
                'open_time': open_time.strftime('%H:%M') if open_time else None,
                'close_time': close_time.strftime('%H:%M') if close_time else None,
            },
            'tables': [{'id': t.id, 'number': t.number, 'table_type': str(t.table_type)} for t in tables],
            'time_slots': time_slots,
            'day_schedule': day_schedule,
            'user_bookings': user_bookings
        })

    def get_week_view(self, date, user, slot_duration):
        start = date - timedelta(days=date.weekday())
        return self._get_calendar_range_view(start, 7, user, slot_duration, 'week')

    def get_month_view(self, date, user, slot_duration):
        start = date.replace(day=1)
        _, last_day = monthrange(start.year, start.month)
        end = start.replace(day=last_day)

        # Расширяем границы по неделям
        start -= timedelta(days=start.weekday())  # к понедельнику
        end += timedelta(days=(6 - end.weekday()))  # к воскресенью
        num_days = (end - start).days + 1

        raw_response = self._get_calendar_range_view(start, num_days, user, slot_duration, 'month')
        days_data = raw_response.data["days"]

        # Добавим информацию о пользовательских бронированиях в каждый день
        for booking in raw_response.data.get("user_bookings", []):
            booking_date = booking['start_time'].split('T')[0]
            if booking_date in days_data:
                if 'user_bookings' not in days_data[booking_date]:
                    days_data[booking_date]['user_bookings'] = []
                days_data[booking_date]['user_bookings'].append(booking)

        # Формируем недели
        sorted_dates = sorted(days_data.keys())
        weeks = []
        current_week = []

        for d in sorted_dates:
            day_obj = days_data[d]
            day_obj['date'] = d  # обязательно проставляем дату
            current_week.append(day_obj)
            if len(current_week) == 7:
                weeks.append(current_week)
                current_week = []

        if current_week:
            weeks.append(current_week)

        raw_response.data["month"] = date.strftime('%Y-%m')
        raw_response.data["year"] = date.year
        raw_response.data["weeks"] = weeks

        return raw_response

    def _get_calendar_range_view(self, start_date, num_days, user, slot_duration, view_type):
        tz = pytz.timezone('Europe/Moscow')
        days = [start_date + timedelta(days=i) for i in range(num_days)]
        tables = Table.objects.filter(is_active=True).order_by('number')
        calendar_schedule = defaultdict(dict)
        time_slots_set = set()

        if user:
            user_bookings_qs = Booking.objects.filter(
                user=user,
                start_time__date__gte=start_date
            )
            user_bookings = [{
                'id': b.id,
                'table_id': b.table_id,
                'start_time': b.start_time.isoformat(),
                'end_time': b.end_time.isoformat(),
                'status': b.get_status_display()
            } for b in user_bookings_qs]
        else:
            user_bookings = []

        for day in days:
            is_working, open_time, close_time, shortened = self.get_open_close_times(day)
            if not is_working:
                calendar_schedule[day.isoformat()] = {
                    'date': day.isoformat(),
                    'is_working_day': False,
                    'shortened': False,
                    'working_hours': None,
                    'day_schedule': {}
                }
                continue

            # Создаём aware datetime с Moscow timezone
            day_start = tz.localize(datetime.combine(day, open_time))
            day_end = tz.localize(datetime.combine(day, close_time))

            # Генерация слотов
            slots = []
            current = day_start
            if day_start.minute != 0:
                next_hour = (day_start + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
                if next_hour > day_end:
                    next_hour = day_end
                slots.append((current, next_hour))
                current = next_hour

            while current < day_end:
                slot_end = current + timedelta(minutes=slot_duration)
                if slot_end > day_end:
                    slots.append((current, day_end))
                    break
                slots.append((current, slot_end))
                current = slot_end

            # Получаем бронирования
            bookings = self.get_bookings(day_start, day_end, user)
            booking_map = defaultdict(list)
            for b in bookings:
                booking_map[b.table_id].append((b.start_time, b.end_time))

            # Цены и акции
            pricing_data = TableTypePricing.objects.select_related('pricing_plan', 'table_type')
            offers = SpecialOffer.objects.filter(
                is_active=True,
                valid_from__lte=day,
                valid_to__gte=day
            ).prefetch_related('tables')

            offers_by_table = defaultdict(list)
            for offer in offers:
                target_tables = tables if offer.apply_to_all else offer.tables.all()
                for table in target_tables:
                    offers_by_table[table.id].append(offer)

            time_slots_for_day = []
            day_schedule = defaultdict(dict)

            for slot_start, slot_end in slots:
                label = slot_start.strftime('%H:%M')
                any_visible = False  # покажем ли этот слот хоть где-то

                for table in tables:
                    overlaps = any(s < slot_end and e > slot_start for s, e in booking_map.get(table.id, []))

                    is_past = slot_end <= timezone.now().astimezone(tz)

                    # Скрываем весь слот, если он в прошлом и пользователь не админ
                    if is_past and not (user and user.is_staff):
                        continue

                    # Учитываем, что слот будет отображён
                    any_visible = True

                    is_user_booking = any(
                        s < slot_end and e > slot_start
                        for s, e in booking_map.get(table.id, [])
                        if user and not user.is_staff and b.user_id == user.id
                    )

                    if overlaps:
                        slot_status = 'booked'
                    elif is_past:
                        slot_status = '-'
                    else:
                        slot_status = 'available'

                    # Цены
                    pricing = None
                    for p in pricing_data:
                        if p.table_type != table.table_type:
                            continue
                        plan = p.pricing_plan
                        if plan.weekdays and str(slot_start.isoweekday()) not in plan.weekdays:
                            continue
                        if plan.time_from and plan.time_to:
                            if not (plan.time_from <= slot_start.time() < plan.time_to):
                                continue
                        pricing = p
                        break

                    duration = (slot_end - slot_start).total_seconds() / 3600
                    base_price = pricing.hour_rate * duration if pricing else 0
                    discount = 0
                    for offer in offers_by_table.get(table.id, []):
                        if str(slot_start.isoweekday()) in offer.weekdays:
                            if not offer.time_from or not offer.time_to or (
                                    offer.time_from <= slot_start.time() < offer.time_to):
                                discount = max(discount, offer.discount_percent)

                    final_price = base_price * (1 - discount / 100)

                    day_schedule[table.id][label] = {
                        'status': slot_status,
                        'is_user_booking': is_user_booking,
                        'start': slot_start.strftime('%H:%M'),
                        'end': slot_end.strftime('%H:%M'),
                        'price': int(final_price),
                        'discount_applied': discount > 0,
                        'discount_percent': discount
                    }

                if any_visible:
                    time_slots_for_day.append(label)
                    time_slots_set.add(label)

            booking_date_str = day.isoformat()
            user_bookings_count = sum(
                1 for b in user_bookings if b['start_time'].startswith(booking_date_str)
            )

            calendar_schedule[day.isoformat()] = {
                'user_bookings': [],
                'date': day.isoformat(),
                'time_slots': time_slots_for_day,
                'is_working_day': True,
                'shortened': shortened,
                'working_hours': {
                    'open_time': open_time.strftime('%H:%M'),
                    'close_time': close_time.strftime('%H:%M'),
                },
                'day_schedule': day_schedule,
                'total_bookings': sum(len(slots) for slots in booking_map.values()),
                'user_bookings_count': user_bookings_count
            }

        return Response({
            'calendar_type': view_type,
            'start_date': start_date.isoformat(),
            'end_date': (start_date + timedelta(days=num_days - 1)).isoformat(),
            'tables': [{'id': t.id, 'number': t.number, 'table_type': str(t.table_type)} for t in tables],
            'time_slots': sorted(time_slots_set),
            'days': calendar_schedule,
            'slot_duration': slot_duration,
            'user_bookings': user_bookings
        })




@require_GET
def get_site_settings(request):
    try:
        # Получаем дату или используем текущую
        date_str = request.GET.get('date')
        today = parse_date(date_str) if date_str else timezone.now().date()

        if not today:
            return JsonResponse({'error': 'Invalid date format', 'status': 'error'}, status=400)

        weekday = today.weekday()
        holiday = Holiday.objects.filter(date=today).first()

        if holiday:
            if holiday.status == 'closed':
                open_time, close_time = None, None
                is_open = False
            elif holiday.status == 'shortened' and holiday.open_time and holiday.close_time:
                open_time = holiday.open_time.strftime('%H:%M')
                close_time = holiday.close_time.strftime('%H:%M')
                is_open = True
            else:
                working_day = WorkingDay.objects.get(day=weekday)
                open_time = working_day.open_time.strftime('%H:%M')
                close_time = working_day.close_time.strftime('%H:%M')
                is_open = working_day.is_open
        else:
            working_day = WorkingDay.objects.get(day=weekday)
            open_time = working_day.open_time.strftime('%H:%M')
            close_time = working_day.close_time.strftime('%H:%M')
            is_open = working_day.is_open

        workdays_data = [
            {
                'day': wd.day,
                'day_name': wd.get_day_display(),
                'open_time': wd.open_time.strftime('%H:%M'),
                'close_time': wd.close_time.strftime('%H:%M'),
                'is_open': wd.is_open
            } for wd in WorkingDay.objects.all().order_by('day')
        ]

        holidays_data = [
            {
                'date': h.date.strftime('%Y-%m-%d'),
                'description': h.description,
                'status': h.status,
                'open_time': h.open_time.strftime('%H:%M') if h.open_time else None,
                'close_time': h.close_time.strftime('%H:%M') if h.close_time else None
            } for h in Holiday.objects.filter(
                date__gte=today,
                date__lte=today + timezone.timedelta(days=90)
            ).order_by('date')
        ]

        return JsonResponse({
            'current_day': {
                'is_holiday': bool(holiday),
                'open_time': open_time,
                'close_time': close_time,
                'is_open': is_open
            },
            'workdays': workdays_data,
            'upcoming_holidays': holidays_data,
            'status': 'success'
        })

    except WorkingDay.DoesNotExist:
        return JsonResponse({'error': 'Working day configuration not found', 'status': 'error'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e), 'status': 'error'}, status=500)


class UserBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            bookings = (
                Booking.objects
                .select_related('table', 'table__table_type')
                .filter(user=request.user)
                .order_by('start_time')
            )

            bookings_data = [
                {
                    'id': booking.id,
                    'date': booking.start_time.date().isoformat(),
                    'start_time': booking.start_time.strftime('%H:%M'),
                    'end_time': booking.end_time.strftime('%H:%M'),
                    'table': booking.table.number,
                    'table_type': booking.table.table_type.name,
                    'status': booking.get_status_display(),
                    'can_cancel': booking.status in ['pending']
                }
                for booking in bookings
            ]

            return Response({'bookings': bookings_data}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'bookings': []}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def create_booking_view(request):
    try:
        table_id = request.GET.get('table_id')
        date_str = request.GET.get('date')
        time_str = request.GET.get('time')  # "08:30"
        duration_minutes = int(request.GET.get('duration', 60))
        participants = int(request.GET.get('participants', 2))
        is_group = participants > 1  # или логика твоего проекта

        equipment_param = request.GET.get('equipment')
        equipment_raw = json.loads(equipment_param) if equipment_param else []

        start_time = make_aware(datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M"))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Неверные входные данные'}, status=400)

    # Получаем объект стола
    try:
        table = Table.objects.select_related('table_type').get(id=table_id)
    except Table.DoesNotExist:
        return JsonResponse({'error': 'Стол не найден'}, status=404)

    end_time = start_time + timedelta(minutes=duration_minutes)

    # Проверка пересечения бронирований
    conflicts = Booking.objects.filter(
        table=table,
        start_time__lt=end_time,
        end_time__gt=start_time,
        status__in=['paid', 'pending']  # или нужные статусы
    )
    if conflicts.exists():
        return JsonResponse({'error': 'Стол уже забронирован в это время'}, status=409)

    # Подготовка оборудования для BookingEngine
    equipment_items = []
    for item in equipment_raw:
        try:
            eq = Equipment.objects.get(id=item['id'])
            quantity = int(item.get('quantity', 1))
            equipment_items.append({'equipment': eq, 'quantity': quantity})
        except (Equipment.DoesNotExist, KeyError, ValueError):
            continue  # можно добавить логику обработки ошибки

    # Создаём Booking через BookingEngine
    engine = BookingEngine(
        user=request.user,
        table=table,
        start_time=start_time,
        duration_minutes=duration_minutes,
        participants=participants,
        equipment_items=equipment_items
    )
    booking = engine.create_booking()

    return JsonResponse({
        'success': True,
        'booking_id': booking.id,
        'status': booking.status,
        'total_price': booking.total_price,
        'start_time': booking.start_time.isoformat(),
        'end_time': booking.end_time.isoformat(),
    })


class CreateBookingView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_modal.html'
    success_url = reverse_lazy('booking-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        timeslot = form.cleaned_data['timeslot']

        # Проверяем доступность слота
        if not timeslot.is_available or timeslot.is_blocked:
            form.add_error(None, 'Выбранный слот недоступен для бронирования')
            return self.form_invalid(form)

        # Устанавливаем слот как занятый
        timeslot.is_available = False
        timeslot.save()

        # Рассчитываем стоимость
        self.calculate_booking_cost(form.instance)

        return super().form_valid(form)

    def calculate_booking_cost(self, booking):
        """Расчет стоимости бронирования"""
        try:
            pricing = TableTypePricing.objects.get(
                table_type=booking.timeslot.table.table_type,
                pricing_plan=booking.timeslot.pricing_plan
            )

            duration = (booking.timeslot.end_time - booking.timeslot.start_time).total_seconds() / 3600

            # Базовая стоимость
            if booking.is_group:
                booking.base_price = pricing.hour_rate_group * duration
            else:
                booking.base_price = pricing.hour_rate * duration

            # Стоимость оборудования
            equipment_price = sum(
                eq.equipment.price_per_hour * duration * eq.quantity
                for eq in booking.bookingequipment_set.all()
            )
            booking.equipment_price = equipment_price

            # Итоговая стоимость
            booking.total_price = booking.base_price + booking.equipment_price

        except Exception as e:
            print(f"Error calculating booking cost: {e}")


class UpdateBookingView(LoginRequiredMixin, UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/update.html'
    success_url = reverse_lazy('management:user_bookings', kwargs={'active_tab': 'bookings'})

    def form_valid(self, form):
        # Пересчитываем стоимость при изменении
        self.calculate_booking_cost(form.instance)
        return super().form_valid(form)

    def calculate_booking_cost(self, booking):
        """Аналогично CreateBookingView"""

@login_required
def get_booking_info(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    table_id = request.GET.get('table_id')
    date_str = request.GET.get('date')
    time_str = request.GET.get('time')
    duration_minutes = request.GET.get('duration', '60')
    is_group = request.GET.get('is_group', 'false').lower() == 'true'

    # Проверяем обязательные параметры
    if not table_id or not date_str or not time_str:
        return JsonResponse({'error': 'Отсутствуют обязательные параметры'}, status=400)

    # Парсим duration_minutes в int с защитой
    try:
        duration_minutes = int(duration_minutes)
    except ValueError:
        return JsonResponse({'error': 'Неверный формат длительности'}, status=400)

    # Парсим equipment JSON, если есть
    equipment_raw = []
    equipment_param = request.GET.get('equipment')
    if equipment_param:
        try:
            equipment_raw = json.loads(equipment_param)
            if not isinstance(equipment_raw, list):
                raise ValueError()
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Неверный формат оборудования'}, status=400)

    # Парсим дату и время в datetime
    try:
        dt_naive = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        dt = make_aware(dt_naive)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Неверный формат даты или времени'}, status=400)

    # Получаем стол

    try:
        table = Table.objects.select_related('table_type').get(id=table_id)
    except Table.DoesNotExist:
        return JsonResponse({'error': 'Стол не найден'}, status=404)

    # Подготавливаем оборудование для BookingEngine
    equipment_items = []
    for item in equipment_raw:
        eq_id = item.get('id')
        if not isinstance(eq_id, int):
            continue
        eq = Equipment.objects.filter(id=eq_id, is_available=True).first()
        if eq:
            quantity = item.get('quantity', 1)
            try:
                quantity = int(quantity)
                if quantity < 1:
                    quantity = 1
            except Exception:
                quantity = 1
            equipment_items.append({'equipment': eq, 'quantity': quantity})

    # Импорт BookingEngine

    engine = BookingEngine(
        user=request.user,
        table=table,
        start_time=dt,
        duration_minutes=duration_minutes,
        participants=table.table_type.max_capacity if not is_group else (table.table_type.max_capacity + 1),
        equipment_items=equipment_items
    )
    engine.calculate_total_price()
    tariff_parts = []

    if engine.pricing_plan:
        tariff_parts.append(engine.pricing_plan.name)

    if engine.special_offer:
        offer_name = engine.special_offer.name  # например, "Ранняя пташка 10% скидка"
        discount = engine.special_offer.discount_percent
        if offer_name and discount:
            tariff_parts.append(f"Акция ({offer_name} {discount}% )")

    tariff_description = " + ".join(tariff_parts) if tariff_parts else "Стандартный тариф"
    if engine.is_group:
        table_price_hour = float(
            engine.pricing.hour_rate_group) if engine.pricing and engine.pricing.hour_rate_group else 0
        table_price_half_hour = float(
            engine.pricing.half_hour_rate_group) if engine.pricing and engine.pricing.half_hour_rate_group else 0
    else:
        table_price_hour = float(engine.pricing.hour_rate) if engine.pricing and engine.pricing.hour_rate else 0
        table_price_half_hour = float(
            engine.pricing.half_hour_rate) if engine.pricing and engine.pricing.half_hour_rate else 0

    # Формируем ответ
    response = {
        'has_membership': bool(engine.membership),
        'membership_name': engine.membership.membership_type.name if engine.membership else None,
        'base_price': engine.base_price,
        'tariff_description': tariff_description,
        'equipment_price': engine.equipment_price,
        'discount': engine.special_offer.discount_percent if engine.special_offer else 0,
        'final_price': engine.total_price,
        'pricing_plan': engine.pricing_plan.name if engine.pricing_plan else 'Не найден',
        'table_number': table.number,
        'table_type_id': table.table_type.id,
        'min_duration': engine.pricing.min_duration if engine.pricing else 30,
        'max_duration': engine.pricing.max_duration if engine.pricing else 180,
        'price_per_hour': table_price_hour,
        'price_per_half_hour': table_price_half_hour,

        'equipment': [
            {
                'id': e.id,
                'name': e.name,
                'price_per_hour': float(e.price_per_hour),
                'price_per_half_hour': float(e.price_per_half_hour),
                'is_available': e.is_available,
                'description': getattr(e, 'description', '')  # если есть описание
            }
            for e in Equipment.objects.filter(is_available=True).order_by('name')
        ],
        'tables': [
            {
                'id': t.id,
                'number': t.number,
                'table_type_display': str(t.table_type),
                'table_type': t.table_type.name,
                'max_capacity': t.table_type.max_capacity,
            }
            for t in Table.objects.filter(is_active=True).order_by('number')
        ],
        'is_group': is_group,
        'duration_minutes': duration_minutes,
    }

    return JsonResponse(response)

@login_required
@require_POST
def cancel_booking(request, booking_id):
    try:
        booking = get_object_or_404(Booking, id=booking_id)

        # Проверяем права: либо пользователь бронирования, либо админ
        if booking.user != request.user and not request.user.is_staff:
            return JsonResponse({'error': 'Недостаточно прав'}, status=403)

        if booking.status not in ['pending', 'paid']:
            return JsonResponse({'error': 'Невозможно отменить бронирование с текущим статусом'}, status=400)

        booking.status = 'cancelled'
        booking.save()

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def booking_rates_api(request):
    try:
        today = date.today()

        # Получаем ВСЕ актуальные тарифные планы
        pricing_plans = PricingPlan.objects.filter(
            Q(valid_from__lte=today),
            Q(valid_to__gte=today) | Q(valid_to__isnull=True)
        ).order_by('-is_default', 'valid_from')

        if not pricing_plans.exists():
            pricing_plans = PricingPlan.objects.filter(is_default=True)
            if not pricing_plans.exists():
                return JsonResponse({'error': 'Тарифные планы не найдены'}, status=404)

        # Получаем все цены для всех найденных тарифных планов
        prices = TableTypePricing.objects.filter(
            pricing_plan__in=pricing_plans
        ).select_related('table_type', 'pricing_plan')

        equipment = Equipment.objects.filter(is_available=True)

        # Формируем ответ с группировкой по тарифным планам
        response_data = {
            'pricing_plans': [],
            'table_types': [],
            'equipment': [],
            'status': 'success'
        }

        # Добавляем информацию о тарифных планах
        for plan in pricing_plans:
            response_data['pricing_plans'].append({
                'id': plan.id,
                'name': plan.name,
                'description': plan.description,
                'valid_from': plan.valid_from.strftime('%Y-%m-%d'),
                'valid_to': plan.valid_to.strftime('%Y-%m-%d') if plan.valid_to else None,
                'is_default': plan.is_default
            })

        # Добавляем информацию о ценах
        for price in prices:
            response_data['table_types'].append({
                'id': price.table_type.id,
                'name': price.table_type.name,
                'pricing_plan_id': price.pricing_plan.id,
                'hour_rate': price.hour_rate,
                'hour_rate_group': price.hour_rate_group,
                'half_hour_rate': price.half_hour_rate,
                'min_duration': price.min_duration,
                'max_duration': price.max_duration
            })

        # Добавляем оборудование
        for item in equipment:
            response_data['equipment'].append({
                'id': item.id,
                'name': item.name,
                'price_per_hour': item.price_per_hour,
                'price_per_half_hour': item.price_per_half_hour
            })

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

@require_GET
def tables_api(request):
    tables = Table.objects.filter(is_active=True).order_by('number')
    tables_data = [{
        'id': table.id,
        'number': table.number,
        'type': table.table_type.name,
        'description': table.description,
        'capacity': table.table_type.max_capacity
    } for table in tables]
    return JsonResponse(tables_data, safe=False)


@csrf_exempt
@require_POST
def calculate_booking_api(request):
    try:
        # Логирование входящего запроса

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        table_id = data.get('table_id')
        duration = int(data.get('duration', 1))
        participants = int(data.get('participants', 2))
        equipment_ids = data.get('equipment', [])

        if not table_id:
            return JsonResponse({'error': 'Table ID is required'}, status=400)

        table = get_object_or_404(Table, id=table_id)

        today = date.today()
        pricing_plan = PricingPlan.objects.filter(
            Q(valid_from__lte=today),
            Q(valid_to__gte=today) | Q(valid_to__isnull=True)
        ).first() or PricingPlan.objects.filter(is_default=True).first()
        if not isinstance(equipment_ids, list):
            return JsonResponse({'error': 'Equipment must be a list'}, status=400)
        if not pricing_plan:
            return JsonResponse({'error': 'Pricing plan not found'}, status=404)

        try:
            pricing = TableTypePricing.objects.get(
                table_type=table.table_type,
                pricing_plan=pricing_plan
            )
        except TableTypePricing.DoesNotExist:
            # Создаем запись с ценами по умолчанию
            pricing, created = TableTypePricing.objects.get_or_create(
                table_type=table.table_type,
                pricing_plan=pricing_plan,
                defaults={
                    'hour_rate': 400,
                    'hour_rate_group': 600,
                    'min_duration': 1,
                    'max_duration': 3
                }
            )

        is_group = participants > table.table_type.max_capacity
        base_rate = pricing.hour_rate_group if is_group else pricing.hour_rate
        table_cost = base_rate * duration

        equipment_items = Equipment.objects.filter(id__in=equipment_ids, is_available=True)
        equipment_cost = sum(e.price_per_hour * duration for e in equipment_items)

        return JsonResponse({
            'table_cost': round(table_cost),
            'equipment_cost': round(equipment_cost),
            'total_cost': round(table_cost + equipment_cost),
            'currency': '₽',
            'is_group': is_group
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


from django.db import transaction


@login_required
@require_POST
def create_booking_api(request):
    try:
        data = json.loads(request.body)

        required_fields = ['date', 'start_time', 'duration', 'table_id']
        missing = [field for field in required_fields if field not in data]
        if missing:
            return JsonResponse({'error': f'Missing required fields: {", ".join(missing)}'}, status=400)

        try:
            start_datetime = make_aware(datetime.strptime(f"{data['date']} {data['start_time']}", "%Y-%m-%d %H:%M"))
        except ValueError:
            return JsonResponse({'error': 'Invalid date or time format'}, status=400)

        try:
            duration_minutes = int(data['duration'])
            if duration_minutes <= 0:
                raise ValueError
        except ValueError:
            return JsonResponse({'error': 'Duration must be a positive integer (minutes)'}, status=400)

        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        table = get_object_or_404(Table, id=data['table_id'])

        overlapping = Booking.objects.filter(
            table=table,
            start_time__lt=end_datetime,
            end_time__gt=start_datetime,
            status__in=['pending', 'paid']
        )
        if overlapping.exists():
            return JsonResponse({'error': 'Стол уже занят на это время'}, status=400)

        equipment_items = []
        for item in data.get('equipment', []):
            try:
                equipment = Equipment.objects.get(id=item['id'])
                quantity = int(item.get('quantity', 1))
                equipment_items.append({'equipment': equipment, 'quantity': quantity})
            except Equipment.DoesNotExist:
                return JsonResponse({'error': f"Invalid equipment ID: {item['id']}"}, status=400)

        promo_code_str = data.get('promo_code')
        promo = None
        if promo_code_str:
            promo = PromoCode.objects.filter(code=promo_code_str, is_active=True).first()

            usage_count = PromoCodeUsage.objects.filter(promo_code=promo, user=request.user).count()
            if usage_count >= promo.max_uses_per_user:
                return JsonResponse({'error': 'Вы уже использовали этот промокод максимально возможное число раз'},
                                    status=400)

    # Также проверка глобального лимита
            if promo.usage_limit is not None and promo.used_count >= promo.usage_limit:
                return JsonResponse({'error': 'Этот промокод уже исчерпал лимит использования'}, status=400)
            if not promo or not (promo.valid_from <= start_datetime.date() <= promo.valid_to):
                return JsonResponse({'error': 'Invalid or expired promo code'}, status=400)

        membership = request.user.memberships.filter(is_active=True).first()
        if membership and not membership.is_valid():
            membership = None

        loyalty_profile = getattr(request.user, 'loyaltyprofile', None)
        pending_bookings_count = Booking.objects.filter(user=request.user, status='pending').count()
        MAX_PENDING_BOOKINGS = getattr(MaxUnpaidBookings.objects.first(), 'max_unpaid_bookings', 2)

        if pending_bookings_count >= MAX_PENDING_BOOKINGS:
            return JsonResponse({
                'error': f'У вас уже есть {MAX_PENDING_BOOKINGS} неоплаченных бронирований. Пожалуйста, оплатите их или отмените, чтобы создать новое.'},
                status=400)

        loyalty_engine = LoyaltyEngine(request.user)

        engine = BookingEngine(
            user=request.user,
            table=table,
            start_time=start_datetime,
            duration_minutes=duration_minutes,
            participants=data.get('participants', 2),
            equipment_items=equipment_items,
            is_group=data.get('is_group', False),
            promo_code=promo
        )
        engine.membership = membership
        engine.loyalty_profile = loyalty_profile
        engine.calculate_total_price()

        with transaction.atomic():
            Booking.objects.filter(status='pending', created_at__lt=now() - timedelta(minutes=10)).delete()

            overlapping = Booking.objects.select_for_update().filter(
                table=table,
                start_time__lt=end_datetime,
                end_time__gt=start_datetime,
                status__in=['pending', 'paid']
            )
            if overlapping.exists():
                return JsonResponse({'error': 'Стол уже занят на это время'}, status=400)

            booking = Booking.objects.create(
                user=request.user,
                table=table,
                start_time=start_datetime,
                end_time=end_datetime,
                participants=data.get('participants', 2),
                is_group=data.get('is_group', False),
                pricing=engine.pricing,
                status='pending',
                promo_code=promo,
                special_offer=engine.special_offer,
            )
            booking.apply_prices_from_engine(engine)
            booking.save()

            if promo:
                promo.used_count = F('used_count') + 1
                promo.save(update_fields=['used_count'])

                PromoCodeUsage.objects.create(
                    promo_code=promo,
                    user=request.user,
                    booking=booking
                )
            if booking.status == 'paid':  # или 'pending' в зависимости от логики
                loyalty_engine.add_points_for_booking(engine.base_price)
            for item in equipment_items:
                BookingEquipment.objects.create(
                    booking=booking,
                    equipment=item['equipment'],
                    quantity=item['quantity']
                )

        return JsonResponse({
            'success': True,
            'booking_id': booking.id,
            'total_price': engine.total_price,
            'base_price': engine.base_price,
            'equipment_price': engine.equipment_price,
            'discount_percent': engine.discount,
            'pricing_plan': str(engine.pricing_plan),
            'promo_code': promo_code_str,
            'promo_code_discount_percent': promo.discount_percent if promo else 0,
            'special_offer': str(engine.special_offer) if engine.special_offer else None,
            'special_offer_discount_percent': engine.special_offer.discount_percent if engine.special_offer else 0,
            'membership_discount_percent': membership.membership_type.discount_percent if membership else 0,
            'loyalty_level': loyalty_profile.level if loyalty_profile else None,
            'loyalty_discount_percent': loyalty_profile.get_discount() if loyalty_profile else Decimal('0.00'),
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

from yookassa import Configuration, Payment
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Настройте ЮКассу (лучше вынести в settings.py)
Configuration.account_id = settings.ACCOUNT_ID
Configuration.secret_key = settings.SHOP_SECRET_KEY


@csrf_exempt
def create_yookassa_payment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Неподдерживаемый метод запроса'}, status=405)

    try:
        data = json.loads(request.body)
        booking_id = data.get('booking_id')
        if not booking_id:
            return JsonResponse({'error': 'Отсутствует booking_id'}, status=400)

        # Получаем бронирование пользователя
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

        # Проверка пересечений
        ACTIVE_STATUSES = ['pending', 'paid']
        conflicts = Booking.objects.filter(
            table=booking.table,
            start_time__lt=booking.end_time,
            end_time__gt=booking.start_time,
            status__in=ACTIVE_STATUSES
        ).exclude(id=booking.id)
        if conflicts.exists():
            return JsonResponse({'error': 'Стол уже забронирован в это время'}, status=409)

        # Проверка на промокод типа "free" и ограничение по использованию
        if booking.promo_code and booking.promo_code.promo_type == 'free':
            usage_count = Booking.objects.filter(
                user=request.user,
                promo_code=booking.promo_code,
                status__in=['pending', 'paid']
            ).exclude(id=booking.id).count()

            max_uses = getattr(booking.promo_code, 'max_uses_per_user', 1) or 1
            if usage_count >= max_uses:
                return JsonResponse({
                    'error': 'Вы уже использовали этот промокод на бесплатное бронирование.'
                }, status=400)

        # Подготовка данных для BookingEngine
        equipment_data = [
            {'equipment': be.equipment, 'quantity': be.quantity}
            for be in booking.bookingequipment_set.all()
        ]

        # Создаем экземпляр BookingEngine с актуальными параметрами
        engine = BookingEngine(
            user=booking.user,
            table=booking.table,
            start_time=booking.start_time,
            duration_minutes=int((booking.end_time - booking.start_time).total_seconds() // 60),
            participants=booking.participants,
            equipment_items=equipment_data,
            is_group=booking.is_group,
            promo_code=booking.promo_code,
            special_offer=booking.special_offer,
            loyalty_profile=getattr(booking, 'loyalty_profile', None),
        )
        engine.calculate_total_price()

        # Обновляем бронирование ценами из движка
        booking.apply_prices_from_engine(engine)
        booking.save()

        # Если итоговая цена 0 — считаем оплачено
        if booking.total_price == 0:
            booking.status = 'paid'
            booking.payment_id = None
            booking.save()
            return JsonResponse({
                'status': 'paid',
                'message': 'Бронирование успешно оплачено промокодом на 100%'
            })

        # Проверка существующего платежа
        if booking.payment_id:
            payment = Payment.find_one(booking.payment_id)
            if payment.status == 'pending':
                return JsonResponse({
                    'payment_id': booking.payment_id,
                    'confirmation_url': payment.confirmation.confirmation_url
                })

        # Создание нового платежа в YooKassa
        return_url = request.build_absolute_uri(
            reverse('bookings:payment_callback', args=[booking.id])
        )

        payment = Payment.create({
            "amount": {
                "value": f"{booking.total_price:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "description": f"Бронирование #{booking.id}",
            "metadata": {
                "booking_id": str(booking.id),
                "user_id": str(request.user.id)
            }
        }, idempotency_key=str(uuid.uuid4()))

        booking.payment_id = payment.id
        booking.status = 'pending'  # Можно явно ставить статус платежа
        booking.save()

        return JsonResponse({
            'payment_id': payment.id,
            'confirmation_url': payment.confirmation.confirmation_url
        })

    except Exception as e:
        return JsonResponse({'error': f'Ошибка при создании платежа: {str(e)}'}, status=500)

def payment_callback(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Проверяем статус бронирования
    if booking.status == 'paid':
        # Можно показать страницу с подтверждением
        messages.success(request, "Оплата прошла успешно! Ваше бронирование подтверждено.")
        # Перенаправляем в профиль (например, на страницу с бронированиями)
        return redirect('/accounts/profile/#my-bookings')  # <-- тут укажи свой URL name для профиля
    else:
        messages.error(request, "Оплата не была завершена или возникла ошибка.")
        return redirect('/accounts/profile/#my-bookings')


@csrf_exempt
def yookassa_webhook(request):
    if request.method != 'POST':
        return HttpResponse(status=405)  # Метод не поддерживается

    try:
        data = json.loads(request.body)
        event = data.get('event')
        payment_object = data.get('object', {})

        # Обрабатываем только успешные оплаты
        if event == 'payment.succeeded':
            payment_id = payment_object.get('id')
            if not payment_id:
                return JsonResponse({'error': 'payment_id отсутствует'}, status=400)

            try:
                booking = Booking.objects.get(payment_id=payment_id)
                booking.status = 'paid'
                booking.save()
            except Booking.DoesNotExist:
                # Если бронирование не найдено, просто игнорируем или логируем
                return JsonResponse({'error': 'Бронирование с таким payment_id не найдено'}, status=404)

        return HttpResponse(status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Некорректный JSON'}, status=400)
    except Exception as e:
        # Логируем ошибку, если нужно
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def equipment_api(request):

    equipment = Equipment.objects.values(
        'id', 'name', 'description', 'price_per_hour', 'price_per_half_hour'
    )
    return JsonResponse(list(equipment), safe=False)