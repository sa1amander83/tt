from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from collections import defaultdict
from calendar import monthrange
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render, get_object_or_404
from datetime import date
from django.urls import reverse_lazy
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView
from django.views.decorators.http import require_GET, require_POST
from django.core.exceptions import ObjectDoesNotExist
import json
from admin_settings.models import WorkingDay, Holiday, SpecialOffer
from events.forms import BookingForm
from .models import Table, Booking, BookingEquipment, Equipment, PricingPlan, TableTypePricing


from .models import Equipment  # не забудь импортировать


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


def get_booking_info(request):
    table_id = request.GET.get('table_id')
    date_str = request.GET.get('date')
    time_str = request.GET.get('time')  # e.g. "08:30"

    try:
        dt = make_aware(datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M"))
    except ValueError:
        return JsonResponse({'error': 'Неверный формат даты или времени'}, status=400)

    table = Table.objects.select_related('table_type').get(id=table_id)
    table_type = table.table_type
    tables = Table.objects.filter(is_active=True).order_by('number')

    active_membership = request.user.memberships.filter(
        is_active=True, start_date__lte=date.today(), end_date__gte=date.today()
    ).first()

    has_membership = bool(active_membership)
    membership_name = active_membership.membership_type.name if has_membership else None

    pricing_plans = PricingPlan.objects.filter(valid_from__lte=dt.date()).order_by('-valid_from')
    applicable_plan = next((plan for plan in pricing_plans if plan.is_applicable(dt)), None) \
                      if pricing_plans else PricingPlan.objects.filter(is_default=True).first()

    pricing = TableTypePricing.objects.filter(table_type=table_type, pricing_plan=applicable_plan).first()

    base_price = pricing.hour_rate if pricing else 0
    min_duration = pricing.min_duration if pricing else 30
    max_duration = pricing.max_duration if pricing else 180

    discount = 0
    special_offers = SpecialOffer.objects.filter(
        is_active=True,
        valid_from__lte=dt.date(),
        valid_to__gte=dt.date(),
    )

    for offer in special_offers:
        if str(dt.isoweekday()) not in offer.weekdays:
            continue
        if offer.time_from and offer.time_to and not (offer.time_from <= dt.time() <= offer.time_to):
            continue
        if not offer.apply_to_all and table not in offer.tables.all():
            continue

        discount = offer.discount_percent
        break

    discounted_price = int(base_price * (1 - discount / 100))

    # 👉 Получение оборудования
    equipment = Equipment.objects.filter(is_available=True)
    equipment_data = [
        {
            'id': e.id,
            'name': e.name,
            'description': e.description,
            'price_per_hour': e.price_per_hour,
            'price_per_half_hour': e.price_per_half_hour,
        } for e in equipment
    ]

    return JsonResponse({
        'has_membership': has_membership,
        'membership_name': membership_name,
        'base_price': base_price,
        'discount': discount,
        'final_price': discounted_price,
        'pricing_plan': applicable_plan.name if applicable_plan else 'Не найден',
        'table_number': table.number,
        'table_type_id': table_type.id,
        'min_duration': min_duration,
        'max_duration': max_duration,
        'tables': [
            {
                'id': t.id,
                'number': t.number,
                'table_type_display': str(t.table_type),
                'table_type': t.table_type.name,
                'max_players': t.table_type.default_capacity,
            } for t in tables
        ],
        'equipment': equipment_data,  # ← 👈 вот сюда добавляем
    })


class CalendarAPIView(APIView):
    permission_classes = [AllowAny]  # Доступ для всех, в том числе анонимных

    def get(self, request, *args, **kwargs):
        view_type = request.query_params.get('view', 'day')
        date_str = request.query_params.get('date')

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
        qs = Booking.objects.filter(start_time__lt=end, end_time__gt=start).select_related('table')
        if user and not (user.is_staff or user.is_superuser):
            qs = qs.filter(user=user)
        return qs

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

        tables = Table.objects.filter(is_active=True).order_by('number')
        start_dt = timezone.make_aware(datetime.combine(date, open_time))
        end_dt = timezone.make_aware(datetime.combine(date, close_time))
        now = timezone.now()

        slots = []
        current = start_dt
        if start_dt.minute != 0:
            next_hour = (start_dt + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            if next_hour > end_dt:
                next_hour = end_dt
            slots.append((start_dt, next_hour))
            current = next_hour
        else:
            current = start_dt

        # Обычные слоты по slot_duration
        while current < end_dt:
            slot_end = current + timedelta(minutes=slot_duration)
            if slot_end > end_dt:
                slots.append((current, end_dt))
                break
            slots.append((current, slot_end))
            current = slot_end

        # Добавим последний слот, если он заканчивается ровно в close_time
        if current < end_dt and current + timedelta(minutes=slot_duration) == end_dt:
            slots.append((current, end_dt))

        bookings = self.get_bookings(start_dt, end_dt, user)

        booking_map = defaultdict(list)
        for b in bookings:
            booking_map[b.table_id].append((b.start_time, b.end_time))

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

        for slot_start, slot_end in slots:
            label = slot_start.strftime('%H:%M')
            time_slots.append(label)

            for table in tables:
                overlaps = any(s < slot_end and e > slot_start for s, e in booking_map.get(table.id, []))
                slot_status = '-' if slot_end <= now else ('Занято' if overlaps else 'available')

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

        return Response({
            'date': date.strftime('%Y-%m-%d'),
            'is_working_day': True,
            'shortened': shortened,
            'weekday': date.weekday(),
            'slot_duration': slot_duration,
            'working_hours': {
                'open_time': open_time.strftime('%H:%M'),
                'close_time': close_time.strftime('%H:%M'),
            },
            'tables': [{'id': t.id, 'number': t.number, 'table_type': str(t.table_type)} for t in tables],
            'time_slots': time_slots,
            'day_schedule': day_schedule
        })

    def get_week_view(self, date, user, slot_duration):
        start = date - timedelta(days=date.weekday())
        return self._get_calendar_range_view(start, 7, user, slot_duration, 'week')

    def get_month_view(self, date, user, slot_duration):
        start = date.replace(day=1)
        _, last_day = monthrange(start.year, start.month)
        end = start.replace(day=last_day)

        # Коррекция начала и конца по неделям
        start -= timedelta(days=start.weekday())
        end += timedelta(days=(6 - end.weekday()))
        num_days = (end - start).days + 1

        raw_response = self._get_calendar_range_view(start, num_days, user, slot_duration, 'month')
        days_data = raw_response.data["days"]

        # Группируем по неделям
        sorted_dates = sorted(days_data.keys())
        weeks = []
        current_week = []

        for d in sorted_dates:
            current_week.append({
                "date": d,
                **days_data[d]
            })
            if len(current_week) == 7:
                weeks.append(current_week)
                current_week = []

        if current_week:  # Последняя неполная неделя
            weeks.append(current_week)

        raw_response.data["month"] = date.strftime('%Y-%m')
        raw_response.data["year"] = date.year
        raw_response.data["weeks"] = weeks

        return raw_response

    def _get_calendar_range_view(self, start_date, num_days, user, slot_duration, view_type):
        days = [start_date + timedelta(days=i) for i in range(num_days)]
        tables = Table.objects.filter(is_active=True).order_by('number')
        calendar_schedule = defaultdict(dict)
        time_slots_set = set()

        for day in days:
            is_working, open_time, close_time, shortened = self.get_open_close_times(day)
            if not is_working:
                calendar_schedule[day.isoformat()] = {
                    'is_working_day': False,
                    'shortened': False,
                    'working_hours': None,
                    'day_schedule': {}
                }
                continue

            day_start = timezone.make_aware(datetime.combine(day, open_time))
            day_end = timezone.make_aware(datetime.combine(day, close_time))
            slots = []
            current = day_start
            if day_start.minute != 0:
                next_hour = (day_start + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
                if next_hour > day_end:
                    next_hour = day_end
                slots.append((day_start, next_hour))
                current = next_hour
            else:
                current = day_start

            while current < day_end:
                slot_end = current + timedelta(minutes=slot_duration)
                if slot_end > day_end:
                    slots.append((current, day_end))
                    break
                slots.append((current, slot_end))
                current = slot_end

            bookings = self.get_bookings(day_start, day_end, user)
            booking_map = defaultdict(list)
            for b in bookings:
                booking_map[b.table_id].append((b.start_time, b.end_time))

            pricing_data = TableTypePricing.objects.select_related('pricing_plan', 'table_type')
            offers = SpecialOffer.objects.filter(is_active=True, valid_from__lte=day,
                                                 valid_to__gte=day).prefetch_related('tables')
            offers_by_table = defaultdict(list)
            for offer in offers:
                target_tables = tables if offer.apply_to_all else offer.tables.all()
                for table in target_tables:
                    offers_by_table[table.id].append(offer)

            time_slots_for_day = []
            day_schedule = defaultdict(dict)

            for slot_start, slot_end in slots:
                label = slot_start.strftime('%H:%M')
                time_slots_set.add(label)
                time_slots_for_day.append(label)

                for table in tables:
                    overlaps = any(s < slot_end and e > slot_start for s, e in booking_map.get(table.id, []))
                    slot_status = 'booked' if overlaps else 'available'

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
                        'start': slot_start.strftime('%H:%M'),
                        'end': slot_end.strftime('%H:%M'),
                        'price': int(final_price),
                        'discount_applied': discount > 0,
                        'discount_percent': discount
                    }

            calendar_schedule[day.isoformat()] = {
                'is_working_day': True,
                'shortened': shortened,
                'working_hours': {
                    'open_time': open_time.strftime('%H:%M'),
                    'close_time': close_time.strftime('%H:%M'),
                },
                'day_schedule': day_schedule
            }

        return Response({
            'calendar_type': view_type,
            'start_date': start_date.isoformat(),
            'end_date': (start_date + timedelta(days=num_days - 1)).isoformat(),
            'tables': [{'id': t.id, 'number': t.number, 'table_type': str(t.table_type)} for t in tables],
            'time_slots': sorted(time_slots_set),
            'days': calendar_schedule,
            'slot_duration': slot_duration
        })




@login_required
def get_booking_info(request):
    table_id = request.GET.get('table_id')
    date_str = request.GET.get('date')
    time_str = request.GET.get('time')  # e.g. "08:30"

    try:
        dt = make_aware(datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M"))
    except ValueError:
        return JsonResponse({'error': 'Неверный формат даты или времени'}, status=400)

    # Стол
    table = Table.objects.select_related('table_type').get(id=table_id)
    table_type = table.table_type
    tables = Table.objects.filter(is_active=True).order_by('number')
    # Абонемент
    active_membership = request.user.memberships.filter(is_active=True, start_date__lte=date.today(),
                                                        end_date__gte=date.today()).first()
    has_membership = bool(active_membership)
    membership_name = active_membership.membership_type.name if has_membership else None

    # Подходящий тарифный план
    pricing_plans = PricingPlan.objects.filter(valid_from__lte=dt.date()).order_by('-valid_from')
    if pricing_plans:
        applicable_plan = next((plan for plan in pricing_plans if plan.is_applicable(dt)), None)
    else:
        applicable_plan = PricingPlan.objects.filter(is_default=True).first()

    #оборудование

    equipment = Equipment.objects.filter(is_available=True).order_by('name')
    # Ценообразование
    pricing = None
    if applicable_plan:
        pricing = TableTypePricing.objects.filter(table_type=table_type, pricing_plan=applicable_plan).first()

    base_price = pricing.hour_rate if pricing else 0
    min_duration = pricing.min_duration if pricing else 30  # в минутах
    max_duration = pricing.max_duration if pricing else 180

    # Применим спецпредложение
    discount = 0
    special_offers = SpecialOffer.objects.filter(
        is_active=True,
        valid_from__lte=dt.date(),
        valid_to__gte=dt.date(),
    )

    for offer in special_offers:
        if str(dt.isoweekday()) not in offer.weekdays:
            continue
        if offer.time_from and offer.time_to and not (offer.time_from <= dt.time() <= offer.time_to):
            continue
        if not offer.apply_to_all and table not in offer.tables.all():
            continue

        discount = offer.discount_percent
        break

    discounted_price = int(base_price * (1 - discount / 100))

    return JsonResponse({
        'has_membership': has_membership,
        'membership_name': membership_name,
        'base_price': base_price,
        'discount': discount,
        'final_price': discounted_price,
        'pricing_plan': applicable_plan.name if applicable_plan else 'Не найден',
        'table_number': table.number,
        'table_type_id': table_type.id,
        'min_duration': min_duration,
        'max_duration': max_duration,
        'equipment': [{'id': e.id, 'name': e.name} for e in equipment],
        'tables': [
            {
                'id': t.id,
                'number': t.number,
                'table_type_display': str(t.table_type),  # что выводится в селекте
                'table_type': t.table_type.name,  # короткое имя
                'max_players': t.table_type.default_capacity,
            } for t in tables
        ],
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


@login_required
def get_user_bookings(request):
    try:
        # Получаем все брони пользователя, отсортированные по времени начала
        bookings = (
            Booking.objects
            .select_related('table', 'table__table_type')  # Оптимизация JOIN'ов
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
                'can_cancel': booking.status in ['pending', 'confirmed']
            }
            for booking in bookings
        ]

        return JsonResponse({'bookings': bookings_data})

    except ObjectDoesNotExist:
        return JsonResponse({'bookings': []})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


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
    success_url = reverse_lazy('booking-list')

    def form_valid(self, form):
        # Пересчитываем стоимость при изменении
        self.calculate_booking_cost(form.instance)
        return super().form_valid(form)

    def calculate_booking_cost(self, booking):
        """Аналогично CreateBookingView"""


@login_required
@require_POST
def cancel_booking(request, booking_id):
    try:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

        if booking.status not in ['pending', 'confirmed']:
            return JsonResponse({'success': False, 'error': 'Невозможно отменить это бронирование'}, status=400)

        # Освобождаем временной слот
        booking.timeslot.is_available = True
        booking.timeslot.save()

        booking.status = 'cancelled'
        booking.save()

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_GET
def booking_rates_api(request):
    try:
        today = date.today()

        # Поиск актуального тарифного плана (с поддержкой open-ended valid_to)
        pricing_plan = (
                PricingPlan.objects.filter(
                    Q(valid_from__lte=today),
                    Q(valid_to__gte=today) | Q(valid_to__isnull=True)
                ).first()
                or PricingPlan.objects.filter(is_default=True).first()
        )

        if not pricing_plan:
            return JsonResponse({'error': 'Тарифный план не найден'}, status=404)

        prices = TableTypePricing.objects.filter(pricing_plan=pricing_plan)
        equipment = Equipment.objects.filter(is_available=True)

        # Формируем ответ
        response_data = {
            'pricing_plan': pricing_plan.name,
            'table_types': [],
            'equipment': [],
            'status': 'success'
        }

        for price in prices:
            response_data['table_types'].append({
                'id': price.table_type.id,
                'name': price.table_type.name,
                'hour_rate': price.hour_rate,
                'hour_rate_group': price.hour_rate_group,
                'min_duration': price.min_duration,
                'max_duration': price.max_duration
            })

        for item in equipment:
            response_data['equipment'].append({
                'id': item.id,
                'name': item.name,
                'price_per_hour': item.price_per_hour
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
        'capacity': table.table_type.default_capacity
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

        is_group = participants > table.table_type.default_capacity
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

        # Парсим дату и время
        try:
            start_datetime = make_aware(datetime.strptime(f"{data['date']} {data['start_time']}", "%Y-%m-%d %H:%M"))
        except ValueError:
            return JsonResponse({'error': 'Invalid date or time format'}, status=400)

        try:
            duration = int(data['duration'])
            if duration <= 0:
                raise ValueError
        except ValueError:
            return JsonResponse({'error': 'Duration must be a positive integer'}, status=400)

        end_datetime = start_datetime + timedelta(hours=duration)

        table = get_object_or_404(Table, id=data['table_id'])

        # Проверка на пересечение с другими бронированиями
        overlapping = Booking.objects.filter(
            table=table,
            start_time__lt=end_datetime,
            end_time__gt=start_datetime,
            status__in=['pending', 'confirmed']
        )
        if overlapping.exists():
            return JsonResponse({'error': 'Timeslot is already booked'}, status=400)

        # Получаем подходящее ценообразование
        today = start_datetime.date()
        pricing = TableTypePricing.objects.filter(
            table_type=table.table_type,
            pricing_plan__valid_from__lte=today
        ).filter(
            Q(pricing_plan__valid_to__gte=today) | Q(pricing_plan__valid_to__isnull=True)
        ).order_by('-pricing_plan__valid_from').first()

        if not pricing:
            return JsonResponse({'error': 'No pricing plan available for this date'}, status=400)

        with transaction.atomic():
            booking = Booking.objects.create(
                user=request.user,
                table=table,
                pricing=pricing,
                start_time=start_datetime,
                end_time=end_datetime,
                participants=data.get('participants', 2),
                is_group=data.get('is_group', False),
                status='pending'
            )

            for equip_id in data.get('equipment', []):
                equipment = get_object_or_404(Equipment, id=equip_id)
                BookingEquipment.objects.create(
                    booking=booking,
                    equipment=equipment,
                    quantity=1
                )

            booking.calculate_prices()
            booking.save()

        return JsonResponse({'success': True, 'booking_id': booking.id})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
