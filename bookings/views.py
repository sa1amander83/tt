from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from datetime import date, timedelta, time, datetime
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.core.exceptions import ValidationError
import json

from admin_settings.models import WorkingDay
from events.forms import BookingForm
from .models import Table, TableType, TimeSlot, Booking, BookingEquipment, Equipment, PricingPlan, TableTypePricing




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
        'current_date': selected_date,
        'view_type': view_type,
        'table_filter': table_filter,
        'status_filter': status_filter,
        'pricing_plan': pricing_plan,
    }
    return render(request, "bookings/bookings.html", context)


@require_GET
def day_view(request):
    selected_date = date.fromisoformat(request.GET.get('date', date.today().isoformat()))
    table_filter = request.GET.get('table', 'all')
    status_filter = request.GET.get('status', 'all')

    tables = Table.objects.filter(is_active=True).order_by('number')
    if table_filter != 'all':
        tables = tables.filter(id=table_filter)

    # Получаем временные слоты из TimeSlot для выбранной даты
    time_slots = TimeSlot.objects.filter(
        start_time__date=selected_date,
        is_available=True,
        is_blocked=False
    ).order_by('start_time')

    bookings = Booking.objects.filter(timeslot__start_time__date=selected_date)
    if status_filter != 'all':
        bookings = bookings.filter(status=status_filter)

    schedule = {}
    for table in tables:
        table_slots = time_slots.filter(table=table)
        for slot in table_slots:
            booking = bookings.filter(timeslot=slot).first()
            schedule[(table.id, slot.start_time.time())] = {
                'slot': slot,
                'booking': booking
            }

    return render(request, "bookings/day_view.html", {
        "tables": tables,
        "time_slots": time_slots,
        "schedule": schedule,
        "date": selected_date,
        "status_filter": status_filter,
    })


@require_GET
def week_view(request):
    selected_date = date.fromisoformat(request.GET.get('date', date.today().isoformat()))
    table_filter = request.GET.get('table', 'all')
    status_filter = request.GET.get('status', 'all')

    start_of_week = selected_date - timedelta(days=selected_date.weekday())
    days_of_week = [start_of_week + timedelta(days=i) for i in range(7)]

    tables = Table.objects.filter(is_active=True).order_by('number')
    if table_filter != 'all':
        tables = tables.filter(id=table_filter)

    bookings = Booking.objects.filter(
        timeslot__start_time__date__range=(start_of_week, days_of_week[-1])
    )
    if status_filter != 'all':
        bookings = bookings.filter(status=status_filter)

    week_schedule = {}
    for table in tables:
        for day in days_of_week:
            day_slots = TimeSlot.objects.filter(
                table=table,
                start_time__date=day,
                is_available=True,
                is_blocked=False
            )
            day_bookings = bookings.filter(timeslot__in=day_slots).order_by('timeslot__start_time')
            week_schedule[(table.id, day)] = day_bookings

    return render(request, "bookings/week_view.html", {
        "tables": tables,
        "days_of_week": days_of_week,
        "week_schedule": week_schedule,
        "start_of_week": start_of_week,
        "status_filter": status_filter,
    })


@require_GET
def month_view(request):
    selected_date = date.fromisoformat(request.GET.get('date', date.today().isoformat()))
    table_filter = request.GET.get('table', 'all')
    status_filter = request.GET.get('status', 'all')

    first_day = selected_date.replace(day=1)
    last_day = (first_day.replace(month=(first_day.month % 12) + 1, day=1) - timedelta(days=1))

    first_weekday = first_day.weekday()
    calendar_start = first_day - timedelta(days=first_weekday)
    last_weekday = last_day.weekday()
    calendar_end = last_day + timedelta(days=(6 - last_weekday))

    weeks = []
    current_day = calendar_start
    while current_day <= calendar_end:
        week = [current_day + timedelta(days=i) for i in range(7)]
        weeks.append(week)
        current_day += timedelta(days=7)

    tables = Table.objects.filter(is_active=True).order_by('number')
    if table_filter != 'all':
        tables = tables.filter(id=table_filter)

    bookings = Booking.objects.filter(
        timeslot__start_time__date__range=(first_day, last_day)
    )
    if status_filter != 'all':
        bookings = bookings.filter(status=status_filter)

    month_schedule = {}
    for table in tables:
        table_bookings = bookings.filter(timeslot__table=table)
        for booking in table_bookings:
            key = (table.id, booking.timeslot.start_time.date())
            month_schedule[key] = booking

    return render(request, "bookings/month_view.html", {
        "weeks": weeks,
        "current_month": selected_date.month,
        "current_year": selected_date.year,
        "tables": tables,
        "month_schedule": month_schedule,
        "status_filter": status_filter,
    })


def get_site_settings(request):
    try:
        settings = WorkingDay.objects.first()


        return JsonResponse({
            'opening_time': {
                'open_time': settings.opening_time,

            },
            'closing_time': {
                'close_time': settings.closing_time,

            }
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
@require_GET
def get_user_bookings(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    bookings = Booking.objects.filter(user=request.user).order_by('timeslot__start_time')

    bookings_data = []
    for booking in bookings:
        bookings_data.append({
            'id': booking.id,
            'date': booking.timeslot.start_time.date().isoformat(),
            'start_time': booking.timeslot.start_time.strftime('%H:%M'),
            'end_time': booking.timeslot.end_time.strftime('%H:%M'),
            'table': booking.timeslot.table.number,
            'table_type': booking.timeslot.table.table_type.name,
            'status': booking.get_status_display(),
            'can_cancel': booking.status in ['pending', 'confirmed']
        })

    return JsonResponse({'bookings': bookings_data})


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


# API views
@require_GET
def booking_rates_api(request):
    try:
        today = date.today()
        pricing_plan = PricingPlan.objects.filter(
            valid_from__lte=today,
            valid_to__gte=today
        ).first() or PricingPlan.objects.filter(is_default=True).first()

        if not pricing_plan:
            return JsonResponse({'error': 'Тарифный план не найден'}, status=404)

        prices = TableTypePricing.objects.filter(pricing_plan=pricing_plan)
        equipment = Equipment.objects.filter(is_available=True)

        response_data = {
            'pricing_plan': pricing_plan.name,
            'table_types': {},
            'equipment': [],
            'status': 'success'
        }

        for price in prices:
            response_data['table_types'][price.table_type.name] = {
                'hour_rate': price.hour_rate,
                'hour_rate_group': price.hour_rate_group,
                'min_duration': price.min_duration,
                'max_duration': price.max_duration
            }

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


@require_GET
def calendar_api(request):
    try:
        status_filter = request.GET.get('status', 'all')
        bookings = Booking.objects.all()

        if status_filter != 'all':
            bookings = bookings.filter(status=status_filter)

        view = request.GET.get('view', 'day')
        date_str = request.GET.get('date')
        table_filter = request.GET.get('table', 'all')

        if view not in ['day', 'week', 'month']:
            return JsonResponse({'error': 'Invalid view type'}, status=400)

        try:
            selected_date = date.fromisoformat(date_str) if date_str else date.today()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'}, status=400)

        tables = Table.objects.filter(is_active=True).order_by('number')
        if table_filter != 'all':
            tables = tables.filter(id=table_filter)

        if view == 'day':
            return day_calendar_api(request, selected_date, tables, status_filter)
        elif view == 'week':
            return week_calendar_api(request, selected_date, tables, status_filter)
        elif view == 'month':
            return month_calendar_api(request, selected_date, tables, status_filter)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

from collections import defaultdict
def month_calendar_api(request, selected_date, tables, status_filter):
    first_day = selected_date.replace(day=1)
    next_month = first_day.replace(month=first_day.month % 12 + 1, day=1) if first_day.month < 12 else first_day.replace(year=first_day.year + 1, month=1, day=1)
    last_day = next_month - timedelta(days=1)

    # Все слоты на месяц
    time_slots = TimeSlot.objects.filter(
        start_time__date__range=(first_day, last_day),
        is_available=True,
        is_blocked=False
    )

    bookings = Booking.objects.filter(timeslot__start_time__date__range=(first_day, last_day))
    if status_filter != 'all':
        bookings = bookings.filter(status=status_filter)

    # Структура расписания
    schedule = defaultdict(list)

    for table in tables:
        table_slots = time_slots.filter(table=table)
        for slot in table_slots:
            day = slot.start_time.date().isoformat()
            booking = bookings.filter(timeslot=slot).first()
            schedule[f"{table.id}-{day}"].append({
                'start': slot.start_time.strftime('%H:%M'),
                'end': slot.end_time.strftime('%H:%M'),
                'booking_id': booking.id if booking else None,
                'status': booking.status if booking else 'available',
                'slot_id': slot.id
            })

    return JsonResponse({
        'view': 'month',
        'month': selected_date.month,
        'year': selected_date.year,
        'tables': [{
            'id': t.id,
            'number': t.number,
            'type': t.table_type.name,
            'capacity': t.table_type.default_capacity
        } for t in tables],
        'schedule': schedule
    })

def week_calendar_api(request, selected_date, tables, status_filter):
    start_of_week = selected_date - timedelta(days=selected_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Загружаем слоты на неделю
    time_slots = TimeSlot.objects.filter(
        start_time__date__range=(start_of_week, end_of_week),
        is_available=True,
        is_blocked=False
    ).order_by('start_time')

    # Загружаем бронирования
    bookings = Booking.objects.filter(timeslot__start_time__date__range=(start_of_week, end_of_week))
    if status_filter != 'all':
        bookings = bookings.filter(status=status_filter)

    # Структура: { "table_id-date": [слоты] }
    schedule = defaultdict(list)

    for table in tables:
        table_slots = time_slots.filter(table=table)
        for slot in table_slots:
            date_str = slot.start_time.date().isoformat()
            booking = bookings.filter(timeslot=slot).first()
            schedule[f"{table.id}-{date_str}"].append({
                'start': slot.start_time.strftime('%H:%M'),
                'end': slot.end_time.strftime('%H:%M'),
                'booking_id': booking.id if booking else None,
                'status': booking.status if booking else 'available',
                'slot_id': slot.id
            })

    return JsonResponse({
        'view': 'week',
        'start_of_week': start_of_week.isoformat(),
        'end_of_week': end_of_week.isoformat(),
        'tables': [{
            'id': t.id,
            'number': t.number,
            'type': t.table_type.name,
            'capacity': t.table_type.default_capacity
        } for t in tables],
        'days': [(start_of_week + timedelta(days=i)).isoformat() for i in range(7)],
        'schedule': schedule
    })

def day_calendar_api(request, selected_date, tables, status_filter):
    time_slots = TimeSlot.objects.filter(
        start_time__date=selected_date,
        is_available=True,
        is_blocked=False
    ).order_by('start_time')

    bookings = Booking.objects.filter(timeslot__start_time__date=selected_date)
    if status_filter != 'all':
        bookings = bookings.filter(status=status_filter)

    schedule = {}
    for table in tables:
        table_slots = time_slots.filter(table=table)
        for slot in table_slots:
            booking = bookings.filter(timeslot=slot).first()
            schedule[f"{table.id}-{slot.start_time.hour}"] = {
                'is_available': booking is None,
                'booking_id': booking.id if booking else None,
                'status': booking.status if booking else 'available',
                'slot_id': slot.id
            }

    return JsonResponse({
        'view': 'day',
        'date': selected_date.isoformat(),
        'tables': [{
            'id': t.id,
            'number': t.number,
            'type': t.table_type.name,
            'capacity': t.table_type.default_capacity
        } for t in tables],
        'time_slots': [t.start_time.strftime('%H:%M') for t in time_slots],
        'schedule': schedule
    })


# Остальные API view (week_calendar_api, month_calendar_api) аналогично адаптируются

@csrf_exempt
@require_POST
def calculate_booking_api(request):
    try:
        # Логирование входящего запроса

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        print("Parsed data:", data)

        table_id = data.get('table_id')
        duration = int(data.get('duration', 1))
        participants = int(data.get('participants', 2))
        equipment_ids = data.get('equipment', [])

        if not table_id:
            return JsonResponse({'error': 'Table ID is required'}, status=400)

        table = get_object_or_404(Table, id=table_id)

        today = date.today()
        pricing_plan = PricingPlan.objects.filter(
            valid_from__lte=today,
            valid_to__gte=today
        ).first() or PricingPlan.objects.filter(is_default=True).first()

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


@login_required
@require_POST
def create_booking_api(request):
    try:
        data = json.loads(request.body)
        required_fields = ['date', 'start_time', 'duration', 'table_id']

        if not all(field in data for field in required_fields):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Получаем временной слот
        start_datetime = datetime.strptime(
            f"{data['date']} {data['start_time']}",
            '%Y-%m-%d %H:%M'
        )
        end_datetime = start_datetime + timedelta(hours=int(data['duration']))

        timeslot = TimeSlot.objects.filter(
            table_id=data['table_id'],
            start_time=start_datetime,
            end_time=end_datetime,
            is_available=True,
            is_blocked=False
        ).first()

        if not timeslot:
            return JsonResponse({'error': 'Timeslot not available'}, status=400)

        # Проверяем, что слот не занят
        if Booking.objects.filter(timeslot=timeslot).exists():
            return JsonResponse({'error': 'Timeslot already booked'}, status=400)

        # Создаем бронирование
        booking = Booking.objects.create(
            user=request.user,
            timeslot=timeslot,
            participants=data.get('participants', 2),
            status='pending'
        )

        # Добавляем оборудование
        for equip_id in data.get('equipment', []):
            equipment = get_object_or_404(Equipment, id=equip_id)
            BookingEquipment.objects.create(
                booking=booking,
                equipment=equipment,
                quantity=1
            )

        # Обновляем доступность слота
        timeslot.is_available = False
        timeslot.save()

        # Рассчитываем стоимость
        booking.calculate_prices()
        booking.save()

        return JsonResponse({
            'success': True,
            'booking_id': booking.id
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)