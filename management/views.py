import json
from datetime import timedelta, datetime, date

from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum, Q, F, Count
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator

from admin_settings.models import Table
from bookings.models import Booking
from buisneslogic.models import Membership

UserModel = get_user_model()

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_staff or self.request.user.is_superuser
        )


class UserProfileView(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request, user_id):
        user = get_object_or_404(UserModel, pk=user_id)

        total_bookings = Booking.objects.filter(user=user).count()
        total_visits = Booking.objects.filter(user=user, status='completed').count()
        total_payments = Booking.objects.filter(
            user=user, status__in=['paid', 'completed']
        ).aggregate(total=Sum('total_price'))['total'] or 0
        cancellations = Booking.objects.filter(user=user, status='cancelled').count()

        recent_bookings = Booking.objects.filter(user=user).order_by('-start_time')[:5]

        now = timezone.now()
        months, visits_data = [], []

        for i in range(5, -1, -1):
            month = now - timedelta(days=30 * i)
            month_start = month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end = (month_start + timedelta(days=32)).replace(day=1)

            visits = Booking.objects.filter(
                user=user, status='completed',
                start_time__gte=month_start, start_time__lt=month_end
            ).count()

            months.append(month.strftime('%b %Y'))
            visits_data.append(visits)

        context = {
            'user_profile': user,
            'total_bookings': total_bookings,
            'total_visits': total_visits,
            'total_payments': total_payments,
            'cancellations': cancellations,
            'recent_bookings': recent_bookings,
            'activity_data': {
                'labels': months,
                'data': visits_data,
            },
        }
        return render(request, 'management/management_templates/users-detail.html', context)


class BookingListView(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request):
        bookings = Booking.objects.select_related('user', 'table').order_by('-created_at')

        date_filter = request.GET.get('date', '')
        status_filter = request.GET.get('status', 'all')
        table_filter = request.GET.get('table', 'all')

        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                bookings = bookings.filter(
                    Q(start_time__date=filter_date) | Q(end_time__date=filter_date)
                )
            except ValueError:
                pass

        if status_filter != 'all':
            bookings = bookings.filter(status=status_filter)

        if table_filter != 'all':
            bookings = bookings.filter(table_id=table_filter)

        paginator = Paginator(bookings, 10)
        page_obj = paginator.get_page(request.GET.get('page'))

        context = {
            'bookings': page_obj,
            'tables': Table.objects.all(),
            'status_choices': dict(Booking.STATUS_CHOICES),
            'filters': {
                'date': date_filter or date.today().strftime('%Y-%m-%d'),
                'status': status_filter,
                'table': table_filter,
            }
        }
        return render(request, 'management/management_templates/bookings.html', context)


class UserListView(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request):
        users = UserModel.objects.all().order_by('-date_joined')

        name_filter = request.GET.get('name', '')
        role_filter = request.GET.get('role', 'all')
        status_filter = request.GET.get('status', 'all')

        if name_filter:
            users = users.filter(
                Q(user_name__icontains=name_filter) |
                Q(email__icontains=name_filter)
            )

        if role_filter != 'all':
            users = users.filter(role=role_filter)

        if status_filter != 'all':
            users = users.filter(status=status_filter)

        paginator = Paginator(users, 10)
        page_obj = paginator.get_page(request.GET.get('page'))

        context = {
            'users': page_obj,
            'roles': UserModel.Role.choices,
            'statuses': [('active', 'Активен'), ('not_active', 'Не активен'), ('blocked', 'Заблокирован')],
            'filters': {
                'name': name_filter,
                'role': role_filter,
                'status': status_filter,
            }
        }
        return render(request, 'management/management_templates/users.html', context)

class ManagementView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'management/management.html'

    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser)



class ReportsView(View):
    template_name = 'reports/reports.html'

    def get(self, request):
        # Получаем параметры фильтрации из GET-запроса
        report_type = request.GET.get('report-type', 'revenue')
        period = request.GET.get('report-period', 'current-month')
        start_date = request.GET.get('report-start-date')
        end_date = request.GET.get('report-end-date')

        # Определяем даты периода
        today = timezone.now().date()
        date_range = self._get_date_range(period, start_date, end_date)

        # Готовим контекст для шаблона
        context = {
            'report_type': report_type,
            'period': period,
            'start_date': date_range['start_date'].strftime('%Y-%m-%d') if date_range['start_date'] else '',
            'end_date': date_range['end_date'].strftime('%Y-%m-%d') if date_range['end_date'] else '',
            'period_name': self._get_period_name(period, date_range),
        }

        # Добавляем данные в зависимости от типа отчета
        if report_type == 'revenue':
            context.update(self._get_revenue_data(date_range))
        elif report_type == 'tables':
            context.update(self._get_tables_data(date_range))
        elif report_type == 'users':
            context.update(self._get_users_data(date_range))
        elif report_type == 'memberships':
            context.update(self._get_memberships_data(date_range))

        return render(request, self.template_name, context)

    def _get_date_range(self, period, custom_start=None, custom_end=None):
        """Определяет диапазон дат на основе выбранного периода"""
        today = timezone.now().date()

        if period == 'current-month':
            start_date = today.replace(day=1)
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        elif period == 'previous-month':
            start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            end_date = today.replace(day=1) - timedelta(days=1)
        elif period == 'quarter':
            current_quarter = (today.month - 1) // 3 + 1
            start_date = datetime(today.year, 3 * current_quarter - 2, 1).date()
            end_date = (datetime(today.year, 3 * current_quarter + 1, 1) - timedelta(days=1)).date()
        elif period == 'year':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        elif period == 'custom' and custom_start and custom_end:
            try:
                start_date = datetime.strptime(custom_start, '%Y-%m-%d').date()
                end_date = datetime.strptime(custom_end, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                start_date = today.replace(day=1)
                end_date = today
        else:
            start_date = today.replace(day=1)
            end_date = today

        return {
            'start_date': start_date,
            'end_date': end_date,
            'prev_period_start': start_date - (end_date - start_date) - timedelta(days=1),
            'prev_period_end': start_date - timedelta(days=1),
        }

    def _get_period_name(self, period, date_range):
        """Возвращает читаемое название периода"""
        if period == 'current-month':
            return date_range['start_date'].strftime('%B %Y')
        elif period == 'previous-month':
            return date_range['start_date'].strftime('%B %Y')
        elif period == 'quarter':
            quarter = (date_range['start_date'].month - 1) // 3 + 1
            return f'{quarter}-й квартал {date_range['start_date'].year}'
        elif period == 'year':
            return str(date_range['start_date'].year)
        else:
            return f"{date_range['start_date'].strftime('%d.%m.%Y')} - {date_range['end_date'].strftime('%d.%m.%Y')}"

    def _get_revenue_data(self, date_range):
        """Собирает данные для отчета по доходам"""
        # Доход от бронирований
        bookings_revenue = Booking.objects.filter(
            start_time__date__gte=date_range['start_date'],
            start_time__date__lte=date_range['end_date'],
            status='paid'
        ).aggregate(total=Sum('total_price'))['total'] or 0

        # Доход от абонементов
        memberships_revenue = Membership.objects.filter(
            created_at__date__gte=date_range['start_date'],
            created_at__date__lte=date_range['end_date'],
            is_active=True
        ).aggregate(total=Sum('price'))['total'] or 0

        # Доход от мероприятий
        events_revenue = Booking.objects.filter(
            date__gte=date_range['start_date'],
            date__lte=date_range['end_date'],
            is_paid=True
        ).aggregate(total=Sum('price'))['total'] or 0

        # Данные за предыдущий период для сравнения
        prev_bookings = Booking.objects.filter(
            start_time__date__gte=date_range['prev_period_start'],
            start_time__date__lte=date_range['prev_period_end'],
            status='paid'
        ).aggregate(total=Sum('total_price'))['total'] or 0
        prev_memberships = Membership.objects.filter(
            created_at__date__gte=date_range['prev_period_start'],
            created_at__date__lte=date_range['prev_period_end'],
            is_active=True
        ).aggregate(total=Sum('price'))['total'] or 0
        prev_events = Booking.objects.filter(
            date__gte=date_range['prev_period_start'],
            date__lte=date_range['prev_period_end'],
            is_paid=True
        ).aggregate(total=Sum('price'))['total'] or 0

        # Процент изменения
        bookings_change = self._calculate_change_percent(bookings_revenue, prev_bookings)
        memberships_change = self._calculate_change_percent(memberships_revenue, prev_memberships)
        events_change = self._calculate_change_percent(events_revenue, prev_events)
        total_change = self._calculate_change_percent(
            bookings_revenue + memberships_revenue + events_revenue,
            prev_bookings + prev_memberships + prev_events
        )

        # Данные для графика по месяцам
        monthly_data = self._get_monthly_revenue_data()

        return {
            'total_revenue': bookings_revenue + memberships_revenue + events_revenue,
            'bookings_revenue': bookings_revenue,
            'memberships_revenue': memberships_revenue,
            'events_revenue': events_revenue,
            'bookings_change': bookings_change,
            'memberships_change': memberships_change,
            'events_change': events_change,
            'total_change': total_change,
            'monthly_data_json': json.dumps(monthly_data, cls=DjangoJSONEncoder),
        }

    def _get_tables_data(self, date_range):
        """Собирает данные для отчета по загрузке столов"""
        # Общая статистика по столам
        total_hours = Booking.objects.filter(
            start_time__date__gte=date_range['start_date'],
            start_time__date__lte=date_range['end_date'],
            status='paid'
        ).annotate(
            duration_hours=(F('end_time') - F('start_time')) / timedelta(hours=1)
        ).aggregate(total=Sum('duration_hours'))['total'] or 0

        # Данные по каждому столу
        tables_data = Table.objects.annotate(
            booking_hours=Sum(
                (F('booking__end_time') - F('booking__start_time')) / timedelta(hours=1),
                filter=Q(
                    booking__start_time__date__gte=date_range['start_date'],
                    booking__start_time__date__lte=date_range['end_date'],
                    booking__status='paid'
                )
            ),
            booking_count=Count(
                'booking',
                filter=Q(
                    booking__start_time__date__gte=date_range['start_date'],
                    booking__start_time__date__lte=date_range['end_date'],
                    booking__status='paid'
                )
            ),
            revenue=Sum(
                'booking__total_price',
                filter=Q(
                    booking__start_time__date__gte=date_range['start_date'],
                    booking__start_time__date__lte=date_range['end_date'],
                    booking__status='paid'
                )
            ),
            cancellations=Count(
                'booking',
                filter=Q(
                    booking__start_time__date__gte=date_range['start_date'],
                    booking__start_time__date__lte=date_range['end_date'],
                    booking__status='cancelled'
                )
            )
        ).order_by('-revenue')

        # Рассчитываем загрузку для каждого стола (в процентах)
        total_possible_hours = ((date_range['end_date'] - date_range[
            'start_date']).days + 1) * 12  # 12 часов работы в день
        for table in tables_data:
            table.usage_percent = round(
                (table.booking_hours or 0) / total_possible_hours * 100) if total_possible_hours else 0

        # Данные для графика
        usage_data = {
            'labels': [table.number for table in tables_data],
            'usage': [table.usage_percent for table in tables_data],
            'revenue': [table.revenue or 0 for table in tables_data],
        }

        return {
            'total_hours': round(total_hours, 1),
            'avg_usage': round(sum(t.usage_percent for t in tables_data) / len(tables_data)) if tables_data else 0,
            'peak_usage': max(t.usage_percent for t in tables_data) if tables_data else 0,
            'most_popular_table': tables_data[0] if tables_data else None,
            'tables_data': tables_data,
            'usage_data_json': json.dumps(usage_data, cls=DjangoJSONEncoder),
        }

    def _get_users_data(self, date_range):
        """Собирает данные по активности пользователей"""
        # Здесь должна быть логика сбора данных по пользователям
        # Возвращаем заглушку для примера
        return {
            'active_users': 0,
            'new_users': 0,
            'repeat_visitors': 0,
        }

    def _get_memberships_data(self, date_range):
        """Собирает данные по абонементам"""
        # Здесь должна быть логика сбора данных по абонементам
        # Возвращаем заглушку для примера
        return {
            'new_memberships': 0,
            'renewed_memberships': 0,
            'active_members': 0,
        }

    def _calculate_change_percent(self, current, previous):
        """Рассчитывает процент изменения между текущим и предыдущим периодом"""
        if previous == 0:
            return 100 if current > 0 else 0
        return round((current - previous) / previous * 100)

    def _get_monthly_revenue_data(self):
        """Собирает данные по доходам за последние 6 месяцев"""
        months = []
        data = {
            'bookings': [],
            'memberships': [],
            'events': [],
            'total': []
        }

        today = timezone.now().date()
        for i in range(6, -1, -1):
            month = today - timedelta(days=30 * i)
            month_start = month.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            months.append(month.strftime('%b %Y'))

            bookings = Booking.objects.filter(
                start_time__date__gte=month_start,
                start_time__date__lte=month_end,
                status='paid'
            ).aggregate(total=Sum('total_price'))['total'] or 0
            data['bookings'].append(bookings)

            memberships = Membership.objects.filter(
                created_at__date__gte=month_start,
                created_at__date__lte=month_end,
                is_active=True
            ).aggregate(total=Sum('price'))['total'] or 0
            data['memberships'].append(memberships)

            events = Booking.objects.filter(
                date__gte=month_start,
                date__lte=month_end,
                is_paid=True
            ).aggregate(total=Sum('price'))['total'] or 0
            data['events'].append(events)

            data['total'].append(bookings + memberships + events)

        return {
            'months': months,
            'data': data
        }