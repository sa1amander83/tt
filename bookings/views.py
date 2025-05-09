from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from datetime import date, timedelta, time, datetime

from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from events.forms import BookingForm
from .models import Tables, Booking
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST


def booking_view(request):
    # Определяем текущий вид (день, неделя, месяц)
    view_type = request.GET.get('view', 'day')

    # Получаем выбранную дату из параметров или используем сегодняшнюю
    selected_date_str = request.GET.get('current_date') or request.GET.get('date')
    if selected_date_str:
        selected_date = date.fromisoformat(selected_date_str)
    else:
        selected_date = date.today()

    # Получаем фильтры
    table_filter = request.GET.get('table', 'all')
    status_filter = request.GET.get('status', 'all')

    # Получаем список всех столов
    tables = Tables.objects.all().order_by('number')

    # Применяем фильтр столов
    if table_filter != 'all':
        tables = tables.filter(id=table_filter)

    # Преобразуем дату в datetime для фильтрации
    start_datetime = datetime.combine(selected_date, time.min)
    end_datetime = datetime.combine(selected_date, time.max)

    context = {
        'tables': tables,
        'current_date': selected_date,  # Передаем в шаблон как current_date
        'view_type': view_type,
        'table_filter': table_filter,
        'status_filter': status_filter,
    }

    return render(request, "bookings/bookings.html", context)

@require_GET
def day_view(request):
    selected_date_str = request.GET.get('date')
    table_filter = request.GET.get('table', 'all')
    status_filter = request.GET.get('status', 'all')

    if selected_date_str:
        selected_date = date.fromisoformat(selected_date_str)
    else:
        selected_date = date.today()

    # Получаем список столов с учетом фильтра
    tables = Tables.objects.all().order_by('number')
    if table_filter != 'all':
        tables = tables.filter(id=table_filter)

    # Генерируем временные слоты с 9:00 до 21:00
    time_slots = [time(hour=h) for h in range(9, 22)]

    # Получаем бронирования на выбранную дату
    bookings = Booking.objects.filter(
        start_time__date=selected_date  # Фильтрация по дате части DateTimeField
    )

    # Применяем фильтр статуса
    if status_filter != 'all':
        bookings = bookings.filter(status=status_filter)

    # Создаем расписание
    schedule = {}
    for table in tables:
        for slot in time_slots:
            booking = bookings.filter(
                table=table,
                start_time__time__lte=slot,  # Используем __time для сравнения времени
                end_time__time__gt=slot
            ).first()
            schedule[(table.id, slot)] = booking



    return render(request, "bookings/day_view.html", {
        "tables": tables,
        "time_slots": time_slots,
        "schedule": schedule,
        "date": selected_date,
        "status_filter": status_filter,
    })


@require_GET
def week_view(request):
    selected_date_str = request.GET.get('date')
    table_filter = request.GET.get('table', 'all')
    status_filter = request.GET.get('status', 'all')

    if selected_date_str:
        selected_date = date.fromisoformat(selected_date_str)
    else:
        selected_date = date.today()

    # Определяем начало недели (понедельник)
    start_of_week = selected_date - timedelta(days=selected_date.weekday())
    days_of_week = [start_of_week + timedelta(days=i) for i in range(7)]

    # Получаем список столов с учетом фильтра
    tables = Tables.objects.all().order_by('number')
    if table_filter != 'all':
        tables = tables.filter(id=table_filter)

    # Получаем бронирования на неделю
    bookings = Booking.objects.filter(
        date__gte=start_of_week,
        date__lte=start_of_week + timedelta(days=6)
    )

    # Применяем фильтр статуса
    if status_filter != 'all':
        bookings = bookings.filter(status=status_filter)

    # Создаем расписание для недели
    week_schedule = {}
    for table in tables:
        for day in days_of_week:
            day_bookings = bookings.filter(table=table, date=day).order_by('start_time')
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
    selected_date_str = request.GET.get('date')
    table_filter = request.GET.get('table', 'all')
    status_filter = request.GET.get('status', 'all')

    if selected_date_str:
        selected_date = date.fromisoformat(selected_date_str)
    else:
        selected_date = date.today()

    # Определяем первый день месяца
    first_day = date(selected_date.year, selected_date.month, 1)

    # Определяем последний день месяца
    if selected_date.month == 12:
        last_day = date(selected_date.year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(selected_date.year, selected_date.month + 1, 1) - timedelta(days=1)

    # Определяем дни для отображения в календаре (включая дни из предыдущего/следующего месяца)
    first_weekday = first_day.weekday()  # 0 - понедельник, 6 - воскресенье
    calendar_start = first_day - timedelta(days=first_weekday)

    last_weekday = last_day.weekday()
    calendar_end = last_day + timedelta(days=(6 - last_weekday))

    # Создаем список недель для календаря
    weeks = []
    current_day = calendar_start
    while current_day <= calendar_end:
        week = []
        for _ in range(7):
            week.append(current_day)
            current_day += timedelta(days=1)
        weeks.append(week)

    # Получаем список столов с учетом фильтра
    tables = Tables.objects.all().order_by('number')
    if table_filter != 'all':
        tables = tables.filter(id=table_filter)

    # Получаем бронирования на месяц
    bookings = Booking.objects.filter(
        date__gte=first_day,
        date__lte=last_day
    )

    # Применяем фильтр статуса
    if status_filter != 'all':
        bookings = bookings.filter(status=status_filter)

    # Создаем расписание для месяца
    month_schedule = {}
    for table in tables:
        table_bookings = bookings.filter(table=table)
        for booking in table_bookings:
            month_schedule[(table.id, booking.date)] = booking

    return render(request, "bookings/month_view.html", {
        "weeks": weeks,
        "current_month": selected_date.month,
        "current_year": selected_date.year,
        "tables": tables,
        "month_schedule": month_schedule,
        "status_filter": status_filter,
    })


@require_GET
def get_user_bookings(request):
    """Возвращает бронирования пользователя в формате JSON"""
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    bookings = Booking.objects.filter(user=user).order_by('start_time')  # Сортируем по start_time

    bookings_data = []
    for booking in bookings:
        bookings_data.append({
            'id': booking.id,
            'date': booking.start_time.date().isoformat(),  # Получаем дату из start_time
            'start_time': booking.start_time.strftime('%H:%M'),
            'end_time': booking.end_time.strftime('%H:%M'),
            'table': booking.table.number,
            'status': booking.get_status_display(),
        })

    return JsonResponse({'bookings': bookings_data})
class CreateBookingView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_modal.html'
    success_url = reverse_lazy('booking-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.timeslot.is_available = False
        form.instance.timeslot.save()
        return super().form_valid(form)


class UpdateBookingView(LoginRequiredMixin, UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/update.html'
    success_url = reverse_lazy('booking-list')


@login_required
@require_POST
def cancel_booking(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)

        if booking.status not in ['pending', 'confirmed']:
            return JsonResponse({'success': False, 'error': 'Невозможно отменить это бронирование'}, status=400)

        booking.status = 'cancelled'
        booking.save()

        return JsonResponse({'success': True})

    except Booking.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Бронирование не найдено'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)