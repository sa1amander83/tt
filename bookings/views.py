import traceback
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
from django.db.models import Q
from collections import defaultdict
from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, get_object_or_404
from datetime import date, timedelta, time, datetime
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.core.exceptions import ValidationError
import json

from admin_settings.models import WorkingDay, Holiday, SpecialOffer
from events.forms import BookingForm
from .models import Table,  Booking, BookingEquipment, Equipment, PricingPlan, TableTypePricing




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
        'cols_class' : f"grid-cols-{len(tables)}",
        'current_date': selected_date,
        'view_type': view_type,
        'table_filter': table_filter,
        'status_filter': status_filter,
        'pricing_plan': pricing_plan,
    }
    return render(request, "bookings/bookings.html", context)


class CalendarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        view = request.query_params.get('view', 'day')
        date_str = request.query_params.get('date')
        user = request.user

        if not date_str:
            return Response({"error": "Missing 'date' parameter"}, status=400)

        date = parse_date(date_str)
        if not date:
            return Response({"error": "Invalid 'date' format, expected YYYY-MM-DD"}, status=400)

        # Для одиночной даты кэш не обязателен, но пусть будет
        working_day_map = self.get_working_day_map([date])
        is_working_day, working_hours = working_day_map[date]

        if view == 'day':
            return self.get_day_view(date, is_working_day, working_hours)
        elif view == 'week':
            return self.get_week_view(date, user)
        elif view == 'month':
            return self.get_month_view(date, user)
        else:
            return Response({"error": "Invalid 'view' parameter"}, status=400)


    def get_working_day_map(self, dates):
        """Возвращает словарь {date: (is_working_day, working_hours)} с кэшированной проверкой"""
        results = {}
        for d in dates:
            results[d] = self.check_working_day(d)
        return results

    def get_open_close_times(self, date):
        holiday = Holiday.objects.filter(date=date).first()
        if holiday:
            if holiday.status == 'closed':
                return False, None, None
            elif holiday.status in ['shortened', 'normal']:
                if holiday.open_time and holiday.close_time:
                    return True, holiday.open_time, holiday.close_time

        weekday = date.weekday()
        working_day = WorkingDay.objects.filter(day=weekday, is_open=True).first()
        if working_day:
            return True, working_day.open_time, working_day.close_time

        return False, None, None

    def get_day_view(self, date):
        is_working_day, open_time, close_time = self.get_open_close_times(date)

        if not is_working_day:
            return Response({
                "date": date.strftime('%Y-%m-%d'),
                "is_working_day": False,
                "working_hours": None,
                "tables": [],
                "time_slots": [],
                "day_schedule": {}
            })

        tables = Table.objects.filter(is_active=True).order_by('number')

        day_start = timezone.make_aware(datetime.combine(date, open_time))
        day_end = timezone.make_aware(datetime.combine(date, close_time))

        slot_step_minutes = 60
        slots = []
        current = day_start
        while current + timedelta(minutes=slot_step_minutes) <= day_end:
            slots.append((current, current + timedelta(minutes=slot_step_minutes)))
            current += timedelta(minutes=slot_step_minutes)

        bookings = Booking.objects.filter(
            start_time__lt=day_end,
            end_time__gt=day_start
        ).select_related('table')

        booking_map = defaultdict(list)
        for b in bookings:
            booking_map[b.table_id].append((b.start_time, b.end_time))

        pricing_plans = PricingPlan.objects.all()
        table_type_pricings = TableTypePricing.objects.select_related('pricing_plan', 'table_type')

        special_offers = SpecialOffer.objects.filter(
            is_active=True,
            valid_from__lte=date,
            valid_to__gte=date
        ).prefetch_related('tables')

        offers_by_table = defaultdict(list)
        for offer in special_offers:
            target_tables = tables if offer.apply_to_all else offer.tables.all()
            for table in target_tables:
                offers_by_table[table.id].append(offer)

        time_slots = []
        day_schedule = defaultdict(dict)

        for slot_start, slot_end in slots:
            slot_label = slot_start.strftime('%H:%M')
            time_slots.append(slot_label)

            for table in tables:
                overlaps = any(
                    s < slot_end and e > slot_start
                    for s, e in booking_map.get(table.id, [])
                )
                slot_status = 'booked' if overlaps else 'available'

                applicable_pricing = None
                for pricing in table_type_pricings:
                    plan = pricing.pricing_plan
                    if pricing.table_type != table.table_type:
                        continue
                    if plan.weekday is not None and int(plan.weekday) != slot_start.weekday():
                        continue
                    if plan.time_from and plan.time_to:
                        if not (plan.time_from <= slot_start.time() < plan.time_to):
                            continue
                    applicable_pricing = pricing
                    break

                duration_hours = (slot_end - slot_start).total_seconds() / 3600
                base_price = applicable_pricing.hour_rate * duration_hours if applicable_pricing else 0
                discount = 0

                for offer in offers_by_table.get(table.id, []):
                    if str(slot_start.isoweekday()) in offer.weekdays:
                        if not offer.time_from or not offer.time_to or (
                                offer.time_from <= slot_start.time() < offer.time_to):
                            discount = max(discount, offer.discount_percent)

                final_price = base_price * (1 - discount / 100)

                day_schedule[table.id][slot_label] = {
                    'status': slot_status,
                    'start': slot_start.strftime('%H:%M'),
                    'end': slot_end.strftime('%H:%M'),
                    'price': int(final_price),
                    'discount_applied': discount > 0,
                    'discount_percent': discount
                }

        response = {
            'date': date.strftime('%Y-%m-%d'),
            'is_working_day': True,
            'working_hours': {
                'open': open_time.strftime('%H:%M'),
                'close': close_time.strftime('%H:%M')
            },
            'tables': [{'id': t.id, 'number': t.number, 'table_type': str(t.table_type)} for t in tables],
            'time_slots': time_slots,
            'day_schedule': day_schedule
        }
        return Response(response)

    def get_week_view(self, date, user):
        start_of_week = date - timedelta(days=date.weekday())
        days = [start_of_week + timedelta(days=i) for i in range(7)]

        tables = Table.objects.filter(is_active=True).order_by('number')

        week_schedule = defaultdict(lambda: defaultdict(dict))
        time_slots_set = set()

        for day in days:
            is_working, open_time, close_time = self.get_open_close_times(day)
            if not is_working:
                continue

            day_start = timezone.make_aware(datetime.combine(day, open_time))
            day_end = timezone.make_aware(datetime.combine(day, close_time))

            slot_step_minutes = 60
            slots = []
            current = day_start
            while current + timedelta(minutes=slot_step_minutes) <= day_end:
                slots.append((current, current + timedelta(minutes=slot_step_minutes)))
                current += timedelta(minutes=slot_step_minutes)

            bookings = Booking.objects.filter(
                start_time__lt=day_end,
                end_time__gt=day_start
            ).select_related('table')

            booking_map = defaultdict(list)
            for b in bookings:
                booking_map[b.table_id].append((b.start_time, b.end_time))

            special_offers = SpecialOffer.objects.filter(
                is_active=True,
                valid_from__lte=day,
                valid_to__gte=day
            ).prefetch_related('tables')

            offers_by_table = defaultdict(list)
            for offer in special_offers:
                target_tables = tables if offer.apply_to_all else offer.tables.all()
                for table in target_tables:
                    offers_by_table[table.id].append(offer)

            for slot_start, slot_end in slots:
                slot_label = slot_start.strftime('%H:%M')
                time_slots_set.add(slot_label)

                for table in tables:
                    overlaps = any(
                        s < slot_end and e > slot_start
                        for s, e in booking_map.get(table.id, [])
                    )
                    slot_status = 'booked' if overlaps else 'available'

                    pricing = TableTypePricing.objects.get(table_type=table.table_type)
                    duration = (slot_end - slot_start).total_seconds() / 3600
                    base_price = pricing.hour_rate * duration
                    discount = 0

                    for offer in offers_by_table.get(table.id, []):
                        if str(slot_start.isoweekday()) in offer.weekdays:
                            if not offer.time_from or not offer.time_to or (
                                    offer.time_from <= slot_start.time() < offer.time_to):
                                discount = max(discount, offer.discount_percent)

                    final_price = base_price * (1 - discount / 100)

                    week_schedule[day.isoformat()][table.id][slot_label] = {
                        'status': slot_status,
                        'start': slot_start.strftime('%H:%M'),
                        'end': slot_end.strftime('%H:%M'),
                        'price': int(final_price),
                        'discount_applied': discount > 0,
                        'discount_percent': discount
                    }

        week_info = []
        for day in days:
            is_working, open_time, close_time = self.get_open_close_times(day)
            week_info.append({
                'date': day.isoformat(),
                'is_working_day': is_working,
                'working_hours': {
                    'open': open_time.strftime('%H:%M') if open_time else None,
                    'close': close_time.strftime('%H:%M') if close_time else None
                } if is_working else None
            })

        week_start_dt = timezone.make_aware(datetime.combine(days[0], time.min))
        week_end_dt = timezone.make_aware(datetime.combine(days[-1], time.max))

        user_bookings = Booking.objects.filter(
            user=user,
            start_time__gte=week_start_dt,
            end_time__lte=week_end_dt
        ).select_related('table').order_by('start_time')

        user_bookings_data = [{
            'id': b.id,
            'date': b.start_time.date().isoformat(),
            'start': b.start_time.strftime('%H:%M'),
            'end': b.end_time.strftime('%H:%M'),
            'table_number': b.table.number,
            'status': b.get_status_display()
        } for b in user_bookings]

        response = {
            'start_of_week': start_of_week.strftime('%Y-%m-%d'),
            'days': week_info,
            'tables': [{'id': t.id, 'number': t.number, 'table_type': str(t.table_type)} for t in tables],
            'time_slots': sorted(time_slots_set),
            'week_schedule': week_schedule,
            'user_bookings': user_bookings_data
        }
        return Response(response)

    def get_month_view(self, date, user):
        start_of_month = date.replace(day=1)
        if start_of_month.month == 12:
            next_month = start_of_month.replace(year=start_of_month.year + 1, month=1, day=1)
        else:
            next_month = start_of_month.replace(month=start_of_month.month + 1, day=1)
        end_of_month = next_month - timedelta(days=1)

        tables = Table.objects.filter(is_active=True).order_by('number')

        days_in_month = [start_of_month + timedelta(days=i) for i in range((end_of_month - start_of_month).days + 1)]

        month_schedule = defaultdict(lambda: defaultdict(dict))
        time_slots_set = set()

        for day in days_in_month:
            is_working, open_time, close_time = self.get_open_close_times(day)
            if not is_working:
                continue

            day_start = timezone.make_aware(datetime.combine(day, open_time))
            day_end = timezone.make_aware(datetime.combine(day, close_time))

            slot_step_minutes = 60
            slots = []
            current = day_start
            while current + timedelta(minutes=slot_step_minutes) <= day_end:
                slots.append((current, current + timedelta(minutes=slot_step_minutes)))
                current += timedelta(minutes=slot_step_minutes)

            bookings = Booking.objects.filter(
                start_time__lt=day_end,
                end_time__gt=day_start
            ).select_related('table')

            booking_map = defaultdict(list)
            for b in bookings:
                booking_map[b.table_id].append((b.start_time, b.end_time))

            special_offers = SpecialOffer.objects.filter(
                is_active=True,
                valid_from__lte=day,
                valid_to__gte=day
            ).prefetch_related('tables')

            offers_by_table = defaultdict(list)
            for offer in special_offers:
                target_tables = tables if offer.apply_to_all else offer.tables.all()
                for table in target_tables:
                    offers_by_table[table.id].append(offer)

            for slot_start, slot_end in slots:
                slot_label = slot_start.strftime('%H:%M')
                time_slots_set.add(slot_label)

                for table in tables:
                    overlaps = any(
                        s < slot_end and e > slot_start
                        for s, e in booking_map.get(table.id, [])
                    )
                    slot_status = 'booked' if overlaps else 'available'

                    pricing = TableTypePricing.objects.get(table_type=table.table_type)
                    duration = (slot_end - slot_start).total_seconds() / 3600
                    base_price = pricing.hour_rate * duration
                    discount = 0

                    for offer in offers_by_table.get(table.id, []):
                        if str(slot_start.isoweekday()) in offer.weekdays:
                            if not offer.time_from or not offer.time_to or (
                                    offer.time_from <= slot_start.time() < offer.time_to):
                                discount = max(discount, offer.discount_percent)

                    final_price = base_price * (1 - discount / 100)

                    month_schedule[day.isoformat()][table.id][slot_label] = {
                        'status': slot_status,
                        'start': slot_start.strftime('%H:%M'),
                        'end': slot_end.strftime('%H:%M'),
                        'price': int(final_price),
                        'discount_applied': discount > 0,
                        'discount_percent': discount
                    }

        month_info = []
        for day in days_in_month:
            is_working, open_time, close_time = self.get_open_close_times(day)
            month_info.append({
                'date': day.isoformat(),
                'is_working_day': is_working,
                'working_hours': {
                    'open': open_time.strftime('%H:%M') if open_time else None,
                    'close': close_time.strftime('%H:%M') if close_time else None
                } if is_working else None
            })

        month_start_dt = timezone.make_aware(datetime.combine(days_in_month[0], time.min))
        month_end_dt = timezone.make_aware(datetime.combine(days_in_month[-1], time.max))

        user_bookings = Booking.objects.filter(
            user=user,
            start_time__gte=month_start_dt,
            end_time__lte=month_end_dt
        ).select_related('table').order_by('start_time')

        user_bookings_data = [{
            'id': b.id,
            'date': b.start_time.date().isoformat(),
            'start': b.start_time.strftime('%H:%M'),
            'end': b.end_time.strftime('%H:%M'),
            'table_number': b.table.number,
            'status': b.get_status_display()
        } for b in user_bookings]

        response = {
            'month': start_of_month.strftime('%Y-%m'),
            'days': month_info,
            'tables': [{'id': t.id, 'number': t.number, 'table_type': str(t.table_type)} for t in tables],
            'time_slots': sorted(time_slots_set),
            'month_schedule': month_schedule,
            'user_bookings': user_bookings_data
        }
        return Response(response)


@require_GET
# def day_view(request):
#     selected_date_str = request.GET.get("date", date.today().isoformat())
#     selected_date = date.fromisoformat(selected_date_str)
#     status_filter = request.GET.get("status", "all")
#     table_filter = request.GET.get("table", "all")
#
#     # определяем рабочий день
#     weekday = selected_date.weekday()
#     is_working_day = False
#     opening_time = time(9, 0)
#     closing_time = time(22, 0)
#
#     try:
#         working_day = WorkingDay.objects.get(day=weekday)
#         is_working_day = working_day.is_open
#         opening_time = working_day.open_time
#         closing_time = working_day.close_time
#     except WorkingDay.DoesNotExist:
#         pass
#
#     holiday = Holiday.objects.filter(date=selected_date).first()
#     if holiday:
#         if holiday.status == "closed":
#             is_working_day = False
#         elif holiday.status == "shortened":
#             if holiday.open_time:
#                 opening_time = holiday.open_time
#             if holiday.close_time:
#                 closing_time = holiday.close_time
#
#     if not is_working_day:
#         return render(request, "bookings/day_view.html", {
#             "tables": [],
#             "time_slots": [],
#             "schedule": {},
#             "selected_date": selected_date,
#             "is_working_day": False,
#             "cols_class": "grid-cols-0",
#             "status_filter": status_filter,
#         })
#
#     # ====== Рабочий день — продолжаем ======
#     tables = Table.objects.filter(is_active=True).order_by("number")
#     if table_filter != "all":
#         tables = tables.filter(id=table_filter)
#
#     # строим временные слоты
#     time_slots = []
#     current = opening_time
#     while current < closing_time:
#         time_slots.append(current)
#         current = (datetime.combine(date.today(), current) + timedelta(hours=1)).time()
#
#     # получаем брони
#     bookings = Booking.objects.filter(
#         timeslot__start_time__date=selected_date,
#         timeslot__table__in=tables,
#         timeslot__is_available=False,
#     )
#     if status_filter != "all":
#         bookings = bookings.filter(status=status_filter)
#
#     # строим расписание
#     schedule = {}
#     for table in tables:
#         table_schedule = {}
#         for slot_time in time_slots:
#             slot_dt = make_aware(datetime.combine(selected_date, slot_time))
#             booking = bookings.filter(
#                 timeslot__table=table,
#                 timeslot__start_time__lte=slot_dt,
#                 timeslot__end_time__gt=slot_dt
#             ).first()
#             table_schedule[slot_time] = booking
#         schedule[table.id] = table_schedule
#
#     return render(request, "bookings/day_view.html", {
#         "tables": tables,
#         "time_slots": time_slots,
#         "schedule": schedule,
#         "selected_date": selected_date,
#         "is_working_day": True,
#         "cols_class": f"grid-cols-{len(tables)}",
#         "status_filter": status_filter,
#     })
#
# @require_GET
# def day_calendar_api(request, selected_date, tables, status_filter):
#     weekday = selected_date.weekday()
#     is_working_day = False
#     opening_time, closing_time = time(9, 0), time(22, 0)
#
#     working_day = WorkingDay.objects.filter(day=weekday).first()
#     holiday = Holiday.objects.filter(date=selected_date).first()
#
#     if working_day:
#         is_working_day = working_day.is_open
#         opening_time, closing_time = working_day.open_time, working_day.close_time
#
#     if holiday:
#         if holiday.status == 'closed':
#             is_working_day = False
#         elif holiday.status == 'shortened':
#             opening_time = holiday.open_time or opening_time
#             closing_time = holiday.close_time or closing_time
#
#     time_slots = []
#     current_dt = datetime.combine(selected_date, opening_time)
#     closing_dt = datetime.combine(selected_date, closing_time)
#     while current_dt < closing_dt:
#         time_slots.append(current_dt.time())
#         current_dt += timedelta(hours=1)
#
#     bookings_qs = Booking.objects.none()
#     if is_working_day:
#         bookings_qs = Booking.objects.filter(
#             timeslot__start_time__date=selected_date,
#             timeslot__is_available=False
#         ).select_related('timeslot', 'timeslot__table')
#         if status_filter != 'all':
#             bookings_qs = bookings_qs.filter(status=status_filter)
#
#     bookings_map = {(b.timeslot.table.id, b.timeslot.start_time.time()): b for b in bookings_qs}
#
#     schedule = {}
#     for table in tables:
#         table_schedule = {}
#         for slot_time in time_slots:
#             booking = bookings_map.get((table.id, slot_time))
#             time_str = slot_time.strftime('%H:%M')
#             table_schedule[time_str] = {
#                 'status': booking.status if booking else 'available',
#                 'booking': {
#                     'id': booking.id,
#                     'status': booking.status
#                 } if booking else None
#             }
#         schedule[table.id] = table_schedule
#
#     return JsonResponse({
#         'view': 'day',
#         'date': selected_date.isoformat(),
#         'is_working_day': is_working_day,
#         'cols_class': f'grid-cols-{len(tables)}',
#         'tables': [{
#             'id': t.id,
#             'number': t.number,
#             'type': t.table_type.name,
#             'capacity': t.table_type.default_capacity
#         } for t in tables],
#         'time_slots': [t.strftime('%H:%M') for t in time_slots],
#         'schedule': schedule
#     })
#
# from datetime import date, timedelta
# from django.http import JsonResponse
# @require_GET
# def week_api_view(request, selected_date, tables, status_filter):
#     try:
#
#         selected_date = date.fromisoformat(request.GET.get('date', date.today().isoformat()))
#         table_filter = request.GET.get('table', 'all')
#         status_filter = request.GET.get('status', 'all')
#
#         start_of_week = selected_date - timedelta(days=selected_date.weekday())
#         end_of_week = start_of_week + timedelta(days=6)
#         days_of_week = [start_of_week + timedelta(days=i) for i in range(7)]
#
#         tables = Table.objects.filter(is_active=True).order_by('number')
#         if table_filter != 'all':
#             try:
#                 table_id = int(table_filter)
#                 tables = tables.filter(id=table_id)
#             except ValueError:
#                 tables = tables.none()
#
#         bookings = Booking.objects.filter(
#             timeslot__start_time__date__range=(start_of_week, end_of_week)
#         )
#         if status_filter != 'all':
#             bookings = bookings.filter(status=status_filter)
#
#         workdays = WorkingDay.objects.all()
#         holidays = Holiday.objects.filter(date__range=(start_of_week, end_of_week))
#
#         week_schedule = {}
#         for table in tables:
#             table_schedule = {}
#             for day in days_of_week:
#                 weekday = day.weekday()
#                 working_day = next((wd for wd in workdays if wd.day == weekday), None)
#                 holiday = next((h for h in holidays if h.date == day), None)
#
#                 is_working_day = working_day.is_open if working_day else False
#                 if holiday:
#                     is_working_day = holiday.status != 'closed'
#
#                 slots = TimeSlot.objects.filter(
#                     table=table,
#                     start_time__date=day,
#                     is_available=True,
#                     is_blocked=False
#                 )
#
#                 booked_slots = bookings.filter(timeslot__in=slots).count()
#                 total_slots = slots.count() if is_working_day else 0
#
#                 table_schedule[day.isoformat()] = {
#                     'is_working_day': is_working_day,
#                     'total_slots': total_slots,
#                     'booked_slots': booked_slots
#                 }
#
#             week_schedule[str(table.id)] = table_schedule
#
#         user_bookings_data = []
#         if request.user.is_authenticated:
#             user_bookings = Booking.objects.filter(
#                 user=request.user,
#                 timeslot__start_time__date__range=(start_of_week, end_of_week)
#             ).order_by('timeslot__start_time')
#
#             user_bookings_data = [
#                 {
#                     "table_id": b.timeslot.table.id,
#                     "table_number": b.timeslot.table.number,
#                     "start_time": b.timeslot.start_time.isoformat(),
#                     "status": b.status
#                 }
#                 for b in user_bookings
#             ]
#
#         return JsonResponse({
#             "days_of_week": [d.isoformat() for d in days_of_week],
#             "tables": list(tables.values('id', 'number', 'table_type')),
#             "week_schedule": week_schedule,
#             "user_bookings": user_bookings_data,
#         })
#     except Exception as e:
#         print('Exception caught!', str(e))
#         print(traceback.format_exc())
#         return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)

# def week_view(request):
#     selected_date = date.fromisoformat(request.GET.get('date', date.today().isoformat()))
#     table_filter = request.GET.get('table', 'all')
#     status_filter = request.GET.get('status', 'all')
#
#     start_of_week = selected_date - timedelta(days=selected_date.weekday())
#     end_of_week = start_of_week + timedelta(days=6)
#     days_of_week = [start_of_week + timedelta(days=i) for i in range(7)]
#
#     tables = Table.objects.filter(is_active=True).order_by('number')
#     if table_filter != 'all':
#         tables = tables.filter(id=table_filter)
#
#     bookings = Booking.objects.filter(
#         timeslot__start_time__date__range=(start_of_week, end_of_week)
#     )
#     if status_filter != 'all':
#         bookings = bookings.filter(status=status_filter)
#
#     workdays = WorkingDay.objects.all()
#     holidays = Holiday.objects.filter(date__range=(start_of_week, end_of_week))
#
#     week_schedule = {}
#     for table in tables:
#         table_schedule = {}
#         for day in days_of_week:
#             weekday = day.weekday()
#             working_day = next((wd for wd in workdays if wd.day == weekday), None)
#             holiday = next((h for h in holidays if h.date == day), None)
#
#             is_working_day = working_day.is_open if working_day else False
#             if holiday:
#                 is_working_day = holiday.status != 'closed'
#
#             slots = TimeSlot.objects.filter(
#                 table=table,
#                 start_time__date=day,
#                 is_available=True,
#                 is_blocked=False
#             )
#
#             booked_slots = bookings.filter(timeslot__in=slots).count()
#             total_slots = slots.count() if is_working_day else 0
#
#             table_schedule[day.isoformat()] = {
#                 'is_working_day': is_working_day,
#                 'total_slots': total_slots,
#                 'booked_slots': booked_slots
#             }
#
#         week_schedule[table.id] = table_schedule
#
#     user_bookings = []
#     if request.user.is_authenticated:
#         user_bookings = Booking.objects.filter(
#             user=request.user,
#             timeslot__start_time__date__range=(start_of_week, end_of_week)
#         ).order_by('timeslot__start_time')
#
#     # Подготавливаем JSON-данные для JS
#     week_data = {
#         "days_of_week": [d.isoformat() for d in days_of_week],
#         "tables": list(tables.values('id', 'number', 'table_type')),
#         "week_schedule": week_schedule,
#     }
#
#     return render(request, "bookings/week_view.html", {
#         "week_data_json": json.dumps(week_data, cls=DjangoJSONEncoder),
#         "user_bookings": user_bookings,
#         "start_of_week": start_of_week,
#         "status_filter": status_filter,
#     })



# @require_GET
# def month_view(request):
#     selected_date = date.fromisoformat(request.GET.get('date', date.today().isoformat()))
#     table_filter = request.GET.get('table', 'all')
#     status_filter = request.GET.get('status', 'all')
#
#     first_day = selected_date.replace(day=1)
#     last_day = date(
#         first_day.year,
#         first_day.month,
#         monthrange(first_day.year, first_day.month)[1]
#     )
#
#     calendar_start = first_day - timedelta(days=first_day.weekday())
#     calendar_end = last_day + timedelta(days=(6 - last_day.weekday()))
#
#     weeks = []
#     current_day = calendar_start
#     while current_day <= calendar_end:
#         week = [(current_day + timedelta(days=i)).isoformat() for i in range(7)]
#         weeks.append(week)
#         current_day += timedelta(days=7)
#
#     tables = Table.objects.filter(is_active=True).order_by('number')
#     if table_filter != 'all':
#         tables = tables.filter(id=table_filter)
#
#     bookings = Booking.objects.filter(
#         timeslot__start_time__date__range=(first_day, last_day)
#     )
#     if status_filter != 'all':
#         bookings = bookings.filter(status=status_filter)
#
#     month_schedule = {}
#     for table in tables:
#         table_bookings = bookings.filter(timeslot__table=table)
#         for booking in table_bookings:
#             key = f"{table.id}-{booking.timeslot.start_time.date().isoformat()}"
#             month_schedule[key] = {
#                 "start_time": booking.timeslot.start_time.strftime("%H:%M"),
#                 "end_time": booking.timeslot.end_time.strftime("%H:%M"),
#                 "status": booking.status
#             }
#
#     return render(request, "bookings/month_view.html", {
#         "weeks": weeks,
#         "current_month": selected_date.month,
#         "current_year": selected_date.year,
#         "tables": tables,
#         "month_schedule": month_schedule,
#         "status_filter": status_filter,
#     })

def get_site_settings(request):
    try:
        # Получаем текущий день недели (0-6, где 0 - понедельник)
        today = timezone.now().date()
        weekday = today.weekday()  # Python: 0=понедельник, 6=воскресенье

        # Проверяем, является ли сегодня праздником
        holiday = Holiday.objects.filter(date=today).first()

        if holiday:
            # Если сегодня праздник с особым режимом работы
            if holiday.status == 'closed':
                opening_time = None
                closing_time = None
            elif holiday.status == 'shortened' and holiday.open_time and holiday.close_time:
                opening_time = holiday.open_time.strftime('%H:%M')
                closing_time = holiday.close_time.strftime('%H:%M')
            else:
                # Обычный режим в праздник - берем стандартное время
                working_day = WorkingDay.objects.get(day=weekday)
                opening_time = working_day.open_time.strftime('%H:%M')
                closing_time = working_day.close_time.strftime('%H:%M')
        else:
            # Обычный рабочий день
            working_day = WorkingDay.objects.get(day=weekday)
            opening_time = working_day.open_time.strftime('%H:%M')
            closing_time = working_day.close_time.strftime('%H:%M')

        # Получаем все рабочие дни для календаря
        workdays = WorkingDay.objects.all().order_by('day')
        workdays_data = [
            {
                'day': w.day,
                'day_name': w.get_day_display(),
                'open_time': w.open_time.strftime('%H:%M'),
                'close_time': w.close_time.strftime('%H:%M'),
                'is_open': w.is_open
            }
            for w in workdays
        ]

        # Получаем ближайшие праздники (на 3 месяца вперед)
        upcoming_holidays = Holiday.objects.filter(
            date__gte=today,
            date__lte=today + timezone.timedelta(days=90)
        ).order_by('date')

        holidays_data = [
            {
                'date': h.date.strftime('%Y-%m-%d'),
                'description': h.description,
                'status': h.status,
                'open_time': h.open_time.strftime('%H:%M') if h.open_time else None,
                'close_time': h.close_time.strftime('%H:%M') if h.close_time else None
            }
            for h in upcoming_holidays
        ]

        return JsonResponse({
            'current_day': {
                'is_holiday': bool(holiday),
                'opening_time': opening_time,
                'closing_time': closing_time,
                'is_open': False if holiday and holiday.status == 'closed' else True
            },
            'workdays': workdays_data,
            'upcoming_holidays': holidays_data,
            'status': 'success'
        })

    except WorkingDay.DoesNotExist:
        return JsonResponse({
            'error': 'Working day configuration not found',
            'status': 'error'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)@require_GET
from django.http import JsonResponse

def get_user_bookings(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    bookings = Booking.objects.filter(user=request.user).order_by('start_time')

    bookings_data = []
    for booking in bookings:
        bookings_data.append({
            'id': booking.id,
            'date': booking.start_time.date().isoformat(),
            'start_time': booking.start_time.strftime('%H:%M'),
            'end_time': booking.end_time.strftime('%H:%M'),
            'table': booking.table.number,
            'table_type': booking.table.table_type.name,
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
from datetime import date, timedelta
from collections import defaultdict
from django.http import JsonResponse
from django.db.models import Prefetch

# def calendar_api(request):
#     try:
#         status_filter = request.GET.get('status', 'all')
#         view = request.GET.get('view', 'day')
#         date_str = request.GET.get('date')
#         table_filter = request.GET.get('table', 'all')
#
#         if view not in ['day', 'week', 'month']:
#             return JsonResponse({'error': 'Invalid view type'}, status=400)
#
#         try:
#             selected_date = date.fromisoformat(date_str) if date_str else date.today()
#         except ValueError:
#             return JsonResponse({'error': 'Invalid date format'}, status=400)
#
#         # Получаем активные столы с предзагрузкой связанной информации
#         tables_qs = Table.objects.filter(is_active=True).select_related('table_type').order_by('number')
#
#         if table_filter != 'all':
#             try:
#                 table_id = int(table_filter)
#                 tables_qs = tables_qs.filter(id=table_id)
#             except ValueError:
#                 return JsonResponse({'error': 'Invalid table filter'}, status=400)
#
#         tables = list(tables_qs)
#
#         if view == 'day':
#             data = day_calendar_logic(selected_date, tables, status_filter, request.user)
#             return JsonResponse(data)
#
#         elif view == 'week':
#             data = week_calendar_logic(selected_date, tables, status_filter, request.user)
#             return JsonResponse(data)
#
#         elif view == 'month':
#             data = month_calendar_logic(selected_date, tables, status_filter, request.user)
#             return JsonResponse(data)
#
#         return JsonResponse({'error': 'View not implemented'}, status=501)
#
#     except Exception as e:
#         import traceback
#         return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


# def day_calendar_logic(selected_date, tables, status_filter, user=None):
#     from collections import defaultdict
#
#     time_slots_qs = TimeSlot.objects.filter(
#         start_time__date=selected_date,
#         is_available=True,
#         is_blocked=False
#     ).select_related('table')
#
#     bookings = Booking.objects.filter(
#         timeslot__start_time__date=selected_date
#     )
#     if status_filter != 'all':
#         bookings = bookings.filter(status=status_filter)
#
#     booking_map = {b.timeslot_id: b for b in bookings}
#     day_schedule = defaultdict(dict)  # сделаем словарь словарей: table_id -> slot_time -> slot_info
#
#     unique_slots = set()
#
#     for slot in time_slots_qs:
#         table_id = slot.table.id
#         slot_time = slot.start_time.strftime('%H:%M')
#         unique_slots.add(slot_time)
#
#         booking = booking_map.get(slot.id)
#
#         if table_id not in day_schedule:
#             day_schedule[table_id] = {}
#
#         day_schedule[table_id][slot_time] = {
#             'slot_id': slot.id,
#             'booking_id': booking.id if booking else None,
#             'status': booking.status if booking else 'available',
#             'start': slot.start_time.strftime('%H:%M'),
#             'end': slot.end_time.strftime('%H:%M'),
#         }
#
#     time_slots_sorted = sorted(unique_slots)
#
#     user_bookings = []
#     if user and user.is_authenticated:
#         user_bookings = Booking.objects.filter(
#             user=user,
#             timeslot__start_time__date=selected_date
#         ).select_related('timeslot', 'timeslot__table')
#
#     user_bookings_data = [{
#         'date': booking.timeslot.start_time.date().isoformat(),
#         'start': booking.timeslot.start_time.strftime('%H:%M'),
#         'end': booking.timeslot.end_time.strftime('%H:%M'),
#         'table_number': booking.timeslot.table.number,
#         'status': booking.get_status_display()
#     } for booking in user_bookings]
#
#     return {
#         'view': 'day',
#         'date': selected_date.isoformat(),
#         'tables': [{
#             'id': table.id,
#             'number': table.number,
#             'table_type': table.table_type.name,
#             'capacity': table.table_type.default_capacity
#         } for table in tables],
#         'time_slots': time_slots_sorted,
#         'day_schedule': day_schedule,
#         'user_bookings': user_bookings_data
#     }
#
#
# def week_calendar_logic(selected_date, tables, status_filter, user=None):
#     start_of_week = selected_date - timedelta(days=selected_date.weekday())
#     end_of_week = start_of_week + timedelta(days=6)
#
#     time_slots = TimeSlot.objects.filter(
#         start_time__date__range=(start_of_week, end_of_week),
#         is_available=True,
#         is_blocked=False,
#         table__in=tables
#     ).select_related('table')
#
#     bookings = Booking.objects.filter(
#         timeslot__in=time_slots
#     )
#     if status_filter != 'all':
#         bookings = bookings.filter(status=status_filter)
#
#     booking_map = {b.timeslot_id: b for b in bookings}
#
#     # Формируем список событий для удобства фронтенда
#     week_schedule = []
#     for slot in time_slots:
#         booking = booking_map.get(slot.id)
#         week_schedule.append({
#             'date': slot.start_time.date().isoformat(),
#             'table_id': slot.table.id,
#             'start': slot.start_time.strftime('%H:%M'),
#             'end': slot.end_time.strftime('%H:%M'),
#             'slot_id': slot.id,
#             'booking_id': booking.id if booking else None,
#             'status': booking.status if booking else 'available',
#             'status_display': booking.get_status_display() if booking else 'Свободно',
#         })
#
#     user_bookings_data = []
#     if user and user.is_authenticated:
#         user_bookings = Booking.objects.filter(
#             user=user,
#             timeslot__start_time__date__range=(start_of_week, end_of_week)
#         ).select_related('timeslot', 'timeslot__table')
#
#         user_bookings_data = [{
#             'date': booking.timeslot.start_time.date().isoformat(),
#             'start': booking.timeslot.start_time.strftime('%H:%M'),
#             'end': booking.timeslot.end_time.strftime('%H:%M'),
#             'table_number': booking.timeslot.table.number,
#             'status': booking.get_status_display(),
#             'booking_id': booking.id,
#         } for booking in user_bookings]
#
#     return {
#         'view': 'week',
#         'start_of_week': start_of_week.isoformat(),
#         'end_of_week': end_of_week.isoformat(),
#         'tables': [{
#             'id': table.id,
#             'number': table.number,
#             'table_type': table.table_type.name,
#             'capacity': table.table_type.default_capacity,
#         } for table in tables],
#         'days': [(start_of_week + timedelta(days=i)).isoformat() for i in range(7)],
#         'week_schedule': week_schedule,
#         'user_bookings': user_bookings_data,
#     }
#
#
# def month_calendar_logic(selected_date, tables, status_filter, user=None):
#     first_day = selected_date.replace(day=1)
#     if first_day.month == 12:
#         next_month = first_day.replace(year=first_day.year + 1, month=1, day=1)
#     else:
#         next_month = first_day.replace(month=first_day.month + 1, day=1)
#     last_day = next_month - timedelta(days=1)
#
#     time_slots = TimeSlot.objects.filter(
#         start_time__date__range=(first_day, last_day),
#         is_available=True,
#         is_blocked=False,
#         table__in=tables
#     ).select_related('table')
#
#     bookings = Booking.objects.filter(
#         timeslot__in=time_slots
#     )
#     if status_filter != 'all':
#         bookings = bookings.filter(status=status_filter)
#
#     booking_map = {b.timeslot_id: b for b in bookings}
#
#     # Формируем события в виде списка для удобства фронтенда
#     schedule = []
#     for slot in time_slots:
#         booking = booking_map.get(slot.id)
#         schedule.append({
#             'date': slot.start_time.date().isoformat(),
#             'table_id': slot.table.id,
#             'start': slot.start_time.strftime('%H:%M'),
#             'end': slot.end_time.strftime('%H:%M'),
#             'slot_id': slot.id,
#             'booking_id': booking.id if booking else None,
#             'status': booking.status if booking else 'available',
#             'status_display': booking.get_status_display() if booking else 'Свободно',
#         })
#
#     user_bookings_data = []
#     if user and user.is_authenticated:
#         user_bookings = Booking.objects.filter(
#             user=user,
#             timeslot__start_time__date__range=(first_day, last_day)
#         ).select_related('timeslot', 'timeslot__table')
#
#         user_bookings_data = [{
#             'date': booking.timeslot.start_time.date().isoformat(),
#             'start': booking.timeslot.start_time.strftime('%H:%M'),
#             'end': booking.timeslot.end_time.strftime('%H:%M'),
#             'table_number': booking.timeslot.table.number,
#             'status': booking.get_status_display(),
#             'booking_id': booking.id,
#         } for booking in user_bookings]
#
#     return {
#         'view': 'month',
#         'month': selected_date.month,
#         'year': selected_date.year,
#         'tables': [{
#             'id': table.id,
#             'number': table.number,
#             'table_type': table.table_type.name,
#             'capacity': table.table_type.default_capacity,
#         } for table in tables],
#         'schedule': schedule,
#         'user_bookings': user_bookings_data,
#     }

# def week_calendar_logic(selected_date, tables, status_filter, user=None):
#     start_of_week = selected_date - timedelta(days=selected_date.weekday())
#     end_of_week = start_of_week + timedelta(days=6)
#
#     time_slots = TimeSlot.objects.filter(
#         start_time__date__range=(start_of_week, end_of_week),
#         is_available=True,
#         is_blocked=False
#     ).select_related('table')
#
#     bookings = Booking.objects.filter(
#         timeslot__start_time__date__range=(start_of_week, end_of_week)
#     ).select_related('timeslot', 'timeslot__table')
#
#     if status_filter != 'all':
#         bookings = bookings.filter(status=status_filter)
#
#     booking_map = {b.timeslot_id: b for b in bookings}
#
#     week_schedule = defaultdict(lambda: defaultdict(list))
#
#     for slot in time_slots:
#         table_id = slot.table.id
#         date_str = slot.start_time.date().isoformat()
#         booking = booking_map.get(slot.id)
#
#         week_schedule[table_id][date_str].append({
#             'start': slot.start_time.strftime('%H:%M'),
#             'end': slot.end_time.strftime('%H:%M'),
#             'slot_id': slot.id,
#             'booking_id': booking.id if booking else None,
#             'status': booking.status if booking else 'available',
#         })
#
#     user_bookings = []
#     if user and user.is_authenticated:
#         user_bookings = Booking.objects.filter(
#             user=user,
#             timeslot__start_time__date__range=(start_of_week, end_of_week)
#         ).select_related('timeslot', 'timeslot__table')
#
#     user_bookings_data = [{
#         'date': booking.timeslot.start_time.date().isoformat(),
#         'start': booking.timeslot.start_time.strftime('%H:%M'),
#         'end': booking.timeslot.end_time.strftime('%H:%M'),
#         'table_number': booking.timeslot.table.number,
#         'status': booking.get_status_display()
#     } for booking in user_bookings]
#
#     return {
#         'view': 'week',
#         'start_of_week': start_of_week.isoformat(),
#         'end_of_week': end_of_week.isoformat(),
#         'tables': [{
#             'id': table.id,
#             'number': table.number,
#             'table_type': table.table_type.name,
#             'capacity': table.table_type.default_capacity
#         } for table in tables],
#         'days': [(start_of_week + timedelta(days=i)).isoformat() for i in range(7)],
#         'week_schedule': week_schedule,
#         'user_bookings': user_bookings_data
#     }

#
# @require_GET
# def calendar_api(request):
#     try:
#         status_filter = request.GET.get('status', 'all')
#         bookings = Booking.objects.all()
#
#         if status_filter != 'all':
#             bookings = bookings.filter(status=status_filter)
#
#         view = request.GET.get('view', 'day')
#         date_str = request.GET.get('date')
#         table_filter = request.GET.get('table', 'all')
#
#         if view not in ['day', 'week', 'month']:
#             return JsonResponse({'error': 'Invalid view type'}, status=400)
#
#         try:
#             selected_date = date.fromisoformat(date_str) if date_str else date.today()
#         except ValueError:
#             return JsonResponse({'error': 'Invalid date format'}, status=400)
#
#         tables = Table.objects.filter(is_active=True).order_by('number')
#         if table_filter != 'all':
#             tables = tables.filter(id=table_filter)
#
#         if view == 'day':
#             return day_calendar_api(request, selected_date, tables, status_filter)
#         elif view == 'week':
#             return week_calendar_api(request, selected_date, tables, status_filter)
#         elif view == 'month':
#             return month_calendar_api(request, selected_date, tables, status_filter)
#
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)
#
# from collections import defaultdict
# @require_GET
# def month_calendar_api(request, selected_date, tables, status_filter):
#     first_day = selected_date.replace(day=1)
#     next_month = first_day.replace(month=first_day.month % 12 + 1, day=1) if first_day.month < 12 else first_day.replace(year=first_day.year + 1, month=1, day=1)
#     last_day = next_month - timedelta(days=1)
#
#     # Все слоты на месяц
#     time_slots = TimeSlot.objects.filter(
#         start_time__date__range=(first_day, last_day),
#         is_available=True,
#         is_blocked=False
#     )
#
#     bookings = Booking.objects.filter(timeslot__start_time__date__range=(first_day, last_day))
#     if status_filter != 'all':
#         bookings = bookings.filter(status=status_filter)
#
#     # Структура расписания
#     schedule = defaultdict(list)
#
#     for table in tables:
#         table_slots = time_slots.filter(table=table)
#         for slot in table_slots:
#             day = slot.start_time.date().isoformat()
#             booking = bookings.filter(timeslot=slot).first()
#             schedule[f"{table.id}-{day}"].append({
#                 'start': slot.start_time.strftime('%H:%M'),
#                 'end': slot.end_time.strftime('%H:%M'),
#                 'booking_id': booking.id if booking else None,
#                 'status': booking.status if booking else 'available',
#                 'slot_id': slot.id
#             })
#
#     return JsonResponse({
#         'view': 'month',
#         'month': selected_date.month,
#         'year': selected_date.year,
#         'tables': [{
#             'id': t.id,
#             'number': t.number,
#             'type': t.table_type.name,
#             'capacity': t.table_type.default_capacity
#         } for t in tables],
#         'schedule': schedule
#     })
#
# @require_GET
#
# def week_calendar_api(request):
#     selected_date = datetime.today().date()
#     start_of_week = selected_date - timedelta(days=selected_date.weekday())
#     end_of_week = start_of_week + timedelta(days=6)
#
#     tables = Table.objects.filter(is_active=True).select_related('table_type')
#
#     time_slots = TimeSlot.objects.filter(
#         start_time__date__range=(start_of_week, end_of_week),
#         is_available=True,
#         is_blocked=False
#     ).select_related('table')
#
#     bookings = Booking.objects.filter(
#         timeslot__start_time__date__range=(start_of_week, end_of_week)
#     ).select_related('timeslot', 'timeslot__table')
#
#     booking_map = {b.timeslot_id: b for b in bookings}
#
#     week_schedule = defaultdict(lambda: defaultdict(list))
#
#     for slot in time_slots:
#         table_id = slot.table.id
#         date_str = slot.start_time.date().isoformat()
#         booking = booking_map.get(slot.id)
#
#         week_schedule[table_id][date_str].append({
#             'start': slot.start_time.strftime('%H:%M'),
#             'end': slot.end_time.strftime('%H:%M'),
#             'slot_id': slot.id,
#             'booking_id': booking.id if booking else None,
#             'status': booking.status if booking else 'available',
#         })
#
#     if request.user.is_authenticated:
#         user_bookings = Booking.objects.filter(
#             user=request.user,
#             timeslot__start_time__date__range=(start_of_week, end_of_week)
#         ).select_related('timeslot', 'timeslot__table')
#     else:
#         user_bookings = []
#
#     user_bookings_data = [{
#         'date': booking.timeslot.start_time.date().isoformat(),
#         'start': booking.timeslot.start_time.strftime('%H:%M'),
#         'end': booking.timeslot.end_time.strftime('%H:%M'),
#         'table_number': booking.timeslot.table.number,
#         'status': booking.get_status_display()
#     } for booking in user_bookings]
#
#     response_data = {
#         'view': 'week',
#         'start_of_week': start_of_week.isoformat(),
#         'end_of_week': end_of_week.isoformat(),
#         'tables': [{
#             'id': table.id,
#             'number': table.number,
#             'table_type': table.table_type.name,
#             'capacity': table.table_type.default_capacity
#         } for table in tables],
#         'days': [(start_of_week + timedelta(days=i)).isoformat() for i in range(7)],
#         'week_schedule': week_schedule,
#         'user_bookings': user_bookings_data
#     }
#
#     return JsonResponse(response_data, safe=False)# def day_calendar_api(request, selected_date, tables, status_filter):
# #     time_slots = TimeSlot.objects.filter(
#         start_time__date=selected_date,
#         is_available=True,
#         is_blocked=False
#     ).order_by('start_time')
#
#     bookings = Booking.objects.filter(timeslot__start_time__date=selected_date)
#     if status_filter != 'all':
#         bookings = bookings.filter(status=status_filter)
#
#     schedule = {}
#     for table in tables:
#         table_slots = time_slots.filter(table=table)
#         for slot in table_slots:
#             time_str = slot.start_time.strftime('%H:%M')
#             booking = bookings.filter(timeslot=slot).first()
#             schedule[f"{table.id}-{time_str}"] = {
#                 'status': booking.status if booking else 'available',
#                 'slot_id': slot.id,
#                 'booking': {
#                     'status': booking.status,
#                     'id': booking.id
#                 } if booking else None
#             }
#
#     return JsonResponse({
#         'view': 'day',
#         'date': selected_date.isoformat(),
#         'tables': [{
#             'id': t.id,
#             'number': t.number,
#             'type': t.table_type.name,
#             'capacity': t.table_type.default_capacity
#         } for t in tables],
#         'time_slots': [t.start_time.strftime('%H:%M') for t in time_slots],
#         'schedule': schedule
#     })

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
