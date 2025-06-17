import json
from datetime import timedelta, datetime, date

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum, Q, F, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from rest_framework.response import Response

from admin_settings.models import Table
from bookings.forms import BookingForm
from bookings.models import Booking, BookingPackage

from management.LoyaltyEngine import LoyaltyEngine
from management.forms import UserAdminForm, MembershipTypeForm, LevelBenefitForm
from management.models import LoyaltyProfile, MembershipType, Membership, LoyaltySettings, LevelBenefit

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
        return render(request, 'management/users_modals/user_profile.html', context)


class ManagementView(LoginRequiredMixin, StaffRequiredMixin, View):
    template_name = 'management/management.html'

    def get(self, request, *args, **kwargs):
        active_tab = kwargs.get('active_tab', 'bookings')
        context = self.get_context_data(active_tab)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and active_tab == 'bookings':
            # Для AJAX-запросов создаем отдельный контекст с фильтрацией
            bookings = Booking.objects.select_related('user', 'table').order_by('-created_at')

            # Применяем фильтры из GET-параметров
            date_filter = request.GET.get('date', '')
            status_filter = request.GET.get('status', 'all')

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

            paginator = Paginator(bookings, 10)
            page_obj = paginator.get_page(request.GET.get('page'))

            context['bookings'] = page_obj
            html = render_to_string('management/bookings_modals/bookings_table.html', context, request=request)
            return JsonResponse({'html': html})

        return render(request, self.template_name, context)
    def get_context_data(self, active_tab):
        context = {
            'active_tab': active_tab,
        }

        if active_tab == 'bookings':
            bookings = Booking.objects.select_related('user', 'table').order_by('-created_at')

            # Фильтрация
            date_filter = self.request.GET.get('date', '')
            status_filter = self.request.GET.get('status', 'all')
            table_filter = self.request.GET.get('table', 'all')

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

            # Пагинация
            paginator = Paginator(bookings, 10)
            page_obj = paginator.get_page(self.request.GET.get('page'))

            context.update({
                'bookings': page_obj,
                'tables': Table.objects.all(),
                'status_choices': dict(Booking.STATUS_CHOICES),
                'filters': {
                    'date': date_filter,  # без default на текущую дату
                    'status': status_filter,
                    'table': table_filter,
                },
                'users': get_user_model().objects.all().order_by('-date_joined'),
            })

        elif active_tab == 'users':
            users = get_user_model().objects.all().order_by('-date_joined')

            # Фильтрация
            name_filter = self.request.GET.get('name', '')
            role_filter = self.request.GET.get('role', 'all')
            status_filter = self.request.GET.get('status', 'all')

            if name_filter:
                users = users.filter(
                    Q(user_name__icontains=name_filter) |
                    Q(email__icontains=name_filter)
                )

            if role_filter != 'all':
                users = users.filter(role=role_filter)

            if status_filter != 'all':
                users = users.filter(status=status_filter)

            # Пагинация
            paginator = Paginator(users, 10)
            page_obj = paginator.get_page(self.request.GET.get('page'))

            context.update({
                'users': page_obj,
                'roles': get_user_model().Role.choices,
                'statuses': [('active', 'Активен'), ('not_active', 'Не активен'), ('blocked', 'Заблокирован')],
                'filters': {
                    'name': name_filter,
                    'role': role_filter,
                    'status': status_filter,
                }
            })
        elif active_tab == 'memberships':
            context.update({
                'membership_types': MembershipType.objects.all(),
                'membership_form': MembershipTypeForm(),
                'promocodes': PromoCode.objects.all().order_by('-used_count'),
                'today': timezone.now().date(),

            })
        elif active_tab == 'loyalty':
            loyalty_levels = []
            for level_code, level_name in LoyaltyProfile.Level.choices:
                benefits = LevelBenefit.objects.filter(level=level_code, is_active=True)
                loyalty_levels.append({
                    'code': level_code,
                    'name': level_name,
                    'benefits': benefits,
                })

            # Профиль текущего пользователя
            engine = LoyaltyEngine(self.request.user)
            profile = engine.profile

            # Список типов бенефитов, которые есть у текущего пользователя
            active_benefits = LevelBenefit.objects.filter(level=profile.level, is_active=True)
            user_benefit_types = set(active_benefits.values_list('benefit_type', flat=True))
            user_benefit_map = {
                benefit_type: True
                for benefit_type in user_benefit_types
            }

            active_benefits = LevelBenefit.objects.filter(level=profile.level, is_active=True)
            user_checked_benefit_types = {
                benefit.benefit_type for benefit in active_benefits
            }
            context.update({
                'loyalty_levels': loyalty_levels,
                'profile': profile,
                'level': profile.level,
                'level_name': profile.get_level_display(),
                'points': profile.points,
                'active_points': profile.get_active_points(),
                'next_level': profile.get_next_level_info(),
                'user_benefit_types': user_benefit_map,
                'user_checked_benefit_types': user_checked_benefit_types,
            })

        elif active_tab == 'reports':
            # Получаем параметры фильтрации из GET-запроса
            report_type = self.request.GET.get('report-type', 'revenue')
            period = self.request.GET.get('report-period', 'current-month')
            start_date = self.request.GET.get('report-start-date')
            end_date = self.request.GET.get('report-end-date')

            # Определяем даты периода
            today = timezone.now().date()
            date_range = self._get_date_range(period, start_date, end_date)

            # Готовим контекст для шаблона
            context.update({
                'report_type': report_type,
                'users': get_user_model().objects.all().order_by('-date_joined'),

                'period': period,
                'start_date': date_range['start_date'].strftime('%Y-%m-%d') if date_range['start_date'] else '',
                'end_date': date_range['end_date'].strftime('%Y-%m-%d') if date_range['end_date'] else '',
                'period_name': self._get_period_name(period, date_range),
            })

            # Добавляем данные в зависимости от типа отчета
            if report_type == 'revenue':
                context.update(self._get_revenue_data(date_range))
            elif report_type == 'tables':
                context.update(self._get_tables_data(date_range))
            elif report_type == 'users':
                context.update(self._get_users_data(date_range))
            elif report_type == 'memberships':
                context.update(self._get_memberships_data(date_range))

        return context

    def post(self, request, *args, **kwargs):
        active_tab = kwargs.get('active_tab', 'bookings')

        if active_tab == 'loyalty_modals':
            points = request.POST.get('points')
            try:
                points = int(points)
                engine = LoyaltyEngine(request.user)
                discount_amount = engine.redeem_points_for_discount(points)

                messages.success(request, f'Списано {points} баллов. Скидка: {discount_amount}')
            except ValueError as e:
                messages.error(request, f'Ошибка: {str(e)}')
            except Exception as e:
                messages.error(request, f'Внутренняя ошибка: {str(e)}')

            return redirect(reverse('management:management', kwargs={'active_tab': 'loyalty_modals'}))

        return self.get(request, *args, **kwargs)

    # Методы для работы с отчетами (перенесены из ReportsView)
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
            return f'{quarter}-й квартал {date_range["start_date"].year}'
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

        # Процент изменения
        bookings_change = self._calculate_change_percent(bookings_revenue, prev_bookings)
        memberships_change = self._calculate_change_percent(memberships_revenue, prev_memberships)
        total_change = self._calculate_change_percent(
            bookings_revenue + memberships_revenue,
            prev_bookings + prev_memberships
        )

        # Данные для графика по месяцам
        monthly_data = self._get_monthly_revenue_data()

        return {
            'total_revenue': bookings_revenue + memberships_revenue,
            'bookings_revenue': bookings_revenue,
            'memberships_revenue': memberships_revenue,
            'bookings_change': bookings_change,
            'memberships_change': memberships_change,
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
        total_possible_hours = ((date_range['end_date'] - date_range['start_date']).days + 1) * 12
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
        new_users = UserModel.objects.filter(
            date_joined__date__gte=date_range['start_date'],
            date_joined__date__lte=date_range['end_date']
        ).count()

        active_users = UserModel.objects.filter(
            last_login__date__gte=date_range['start_date'],
            last_login__date__lte=date_range['end_date']
        ).count()

        repeat_users = UserModel.objects.annotate(
            booking_count=Count(
                'booking',
                filter=Q(
                    booking__start_time__date__gte=date_range['start_date'],
                    booking__start_time__date__lte=date_range['end_date'],
                    booking__status='paid'
                )
            )
        ).filter(booking_count__gt=1).count()

        return {
            'active_users': active_users,
            'new_users': new_users,
            'repeat_users': repeat_users,
        }

    def _get_memberships_data(self, date_range):
        """Собирает данные по абонементам"""
        new_memberships = Membership.objects.filter(
            created_at__date__gte=date_range['start_date'],
            created_at__date__lte=date_range['end_date']
        ).count()

        renewed_memberships = Membership.objects.filter(
            renewed_at__date__gte=date_range['start_date'],
            renewed_at__date__lte=date_range['end_date']
        ).count()

        active_members = Membership.objects.filter(
            is_active=True
        ).count()

        return {
            'new_memberships': new_memberships,
            'renewed_memberships': renewed_memberships,
            'active_members': active_members,
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

            data['total'].append(bookings + memberships)

        return {
            'months': months,
            'data': data
        }


class ManagementBookingsAjaxView(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        status = request.GET.get('status', 'all')
        date_filter = request.GET.get('date', None)

        bookings = Booking.objects.select_related('user', 'table').order_by('-created_at')

        if status != 'all':
            bookings = bookings.filter(status=status)

        if date_filter:
            try:
                # Преобразуем строку даты в datetime объект
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                bookings = bookings.filter(
                    start_time__date=filter_date
                )
            except ValueError:
                # Если дата в неправильном формате, игнорируем фильтр
                pass

        paginator = Paginator(bookings, 10)
        page_obj = paginator.get_page(request.GET.get('page'))

        context = {
            'bookings': page_obj,
        }

        return render(request, 'management/bookings_modals/bookings_table.html', context)

from django.views.generic import DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import View


class SingleBookingView(LoginRequiredMixin, UpdateView):
    """Просмотр деталей конкретного бронирования"""
    model = Booking
    form_class = BookingForm  # или просто 'fields = [...]'
    template_name = 'management/bookings_modals/booking_form.html'
    context_object_name = 'booking'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = get_user_model().objects.all()
        return context

    def form_valid(self, form):
        messages.success(self.request, "Бронирование успешно обновлено.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('management:booking_detail', kwargs={'pk': self.object.pk})


class BookingUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование бронирования"""
    model = Booking
    form_class = BookingForm  # Укажите вашу форму для бронирования
    template_name = 'management/bookings_modals/booking_form.html'

    def get_success_url(self):
        return reverse_lazy('management:user_bookings', kwargs={'active_tab': 'bookings'})

    def get_queryset(self):
        # Для администраторов разрешаем редактировать все бронирования
        if self.request.user.is_staff:
            return Booking.objects.all()
        # Для обычных пользователей - только их бронирования
        return Booking.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Бронирование успешно обновлено")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = get_user_model().objects.all()
        return context


class BookingDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление бронирования"""
    model = Booking
    template_name = 'management/bookings_modals/booking_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('management:user_bookings', kwargs={'active_tab': 'bookings'})

    def get_queryset(self):
        # Для администраторов разрешаем удалять все бронирования
        if self.request.user.is_staff:
            return Booking.objects.all()
        # Для обычных пользователей - только их бронирования
        return Booking.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Бронирование успешно удалено")
        return super().delete(request, *args, **kwargs)


class BookingCancelView(LoginRequiredMixin, View):
    """Отмена бронирования (меняет статус вместо удаления)"""

    def post(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=kwargs['pk'])

        # Проверка прав доступа
        if not request.user.is_staff and booking.user != request.user:
            return redirect('permission_denied')

        # Логика отмены бронирования
        booking.status = 'cancelled'
        booking.save()

        # Можно добавить отправку уведомления и т.д.
        messages.success(request, "Бронирование успешно отменено")

        return redirect('management:user_bookings', active_tab='bookings')


class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = get_user_model()
    form_class = UserAdminForm
    template_name = 'management/users_modals/user_form.html'
    success_url = reverse_lazy('management:management', kwargs={'active_tab': 'users'})

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = False
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Пользователь {self.object.email} успешно создан")

        # Дополнительные действия после создания пользователя
        # Например, отправка email с приветствием
        # send_welcome_email(self.object)

        return response

    def form_invalid(self, form):
        messages.error(self.request, "Ошибка при создании пользователя")
        return super().form_invalid(form)


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserModel
    form_class = UserAdminForm
    template_name = 'management/users_modals/user_form.html'
    context_object_name = 'user_obj'

    def test_func(self):
        return self.request.user.is_staff  # Только для администраторов

    def get_success_url(self):
        messages.success(self.request, "Данные пользователя успешно обновлены")
        return reverse_lazy('management:user_profile', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def form_valid(self, form):
        # Дополнительная логика перед сохранением
        response = super().form_valid(form)
        # Можно добавить дополнительные действия после сохранения
        return response


class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = UserModel
    template_name = 'management/users_modals/user_confirm_delete.html'
    success_url = reverse_lazy('management:management:', kwargs={'active_tab': 'users'})

    def test_func(self):
        return self.request.user.is_staff and self.request.user != self.get_object()

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Пользователь успешно удален")
        return super().delete(request, *args, **kwargs)


def fmt(dt, fmt_str='%d.%m.%Y %H:%M'):
    return localtime(dt).strftime(fmt_str) if dt else '—'


class AdminUserProfileView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = get_user_model()
    template_name = 'management/users_modals/user_profile.html'
    context_object_name = 'user_profile'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_object(self, queryset=None):
        user_id = self.kwargs.get('pk')
        return get_object_or_404(get_user_model(), pk=user_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object  # avoids extra DB hit

        # Бронирования
        bookings = Booking.objects.filter(user=user).select_related(
            'table', 'promo_code', 'special_offer', 'pricing'
        ).prefetch_related('equipment').order_by('-start_time')

        context['bookings'] = [{
            'id': b.id,
            'start_date': fmt(b.start_time, '%d.%m.%Y'),
            'start_time': fmt(b.start_time, '%H:%M'),
            'end_time': fmt(b.end_time, '%H:%M'),
            'table': str(b.table),
            'status': b.get_status_display(),
            'participants': b.participants,
            'is_group': b.is_group,
            'base_price': b.base_price,
            'equipment_price': b.equipment_price,
            'total_price': b.total_price,
            'promo_code': b.promo_code.code if b.promo_code else None,
            'special_offer': b.special_offer.name if b.special_offer else None,
            'equipment': [eq.name for eq in b.equipment.all()],
            'notes': b.notes,
            'created_at': fmt(b.created_at),
            'updated_at': fmt(b.updated_at),
            'expires_at': fmt(b.expires_at),
        } for b in bookings]

        # Пакеты бронирования
        packages = BookingPackage.objects.filter(user=user)
        context['booking_packages'] = [{
            'name': pkg.name,
            'total_minutes': pkg.total_minutes,
            'used_minutes': pkg.used_minutes,
            'remaining_minutes': pkg.remaining_minutes(),
            'valid_until': fmt(pkg.valid_until, '%d.%m.%Y'),
            'is_active': pkg.is_valid(),
        } for pkg in packages]

        # Лояльность
        loyalty = LoyaltyProfile.objects.filter(user=user).first()
        if loyalty:
            level_thresholds = LoyaltyProfile.LEVEL_THRESHOLDS
            next_level = None

            for lvl, threshold in sorted(level_thresholds.items(), key=lambda x: x[1]):
                if threshold > loyalty.points:
                    next_level = {'name': lvl, 'points': threshold}
                    break

            points_to_next = (next_level['points'] - loyalty.points) if next_level else 0
            progress_percent = int(loyalty.points / next_level['points'] * 100) if next_level and next_level[
                'points'] > 0 else 100

            context['loyalty_data'] = {
                'level': loyalty.get_level_display(),
                'points': loyalty.points,
                'joined_at': fmt(loyalty.joined_at, '%d.%m.%Y'),
                'discount': float(loyalty.get_discount()),
                'next_level': next_level['name'] if next_level else None,
                'points_to_next': points_to_next,
                'progress_percent': progress_percent,
                'birthday_bonus_used': loyalty.birthday_bonus_used,
                'free_training_used': loyalty.free_training_used,
                'last_free_training_date': fmt(loyalty.last_free_training_date, '%d.%m.%Y'),
            }
        else:
            context['loyalty_data'] = None

        return context


class AdminUserProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = get_user_model()
    form_class = UserAdminForm
    template_name = 'management/users_modals/user_form.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'user_obj'

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        messages.success(self.request, "Профиль пользователя успешно обновлён.")
        return reverse_lazy("management:user_profile", kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        return get_object_or_404(get_user_model(), pk=self.kwargs['pk'])

    def form_valid(self, form):
        form.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'user_name': form.instance.user_name,
                'email': form.instance.email,
                'phone': form.instance.phone,
                'role': form.instance.role
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data()
            }, status=400)
        return super().form_invalid(form)


class UserStatusMixin(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Общая логика для смены статуса пользователя
    """
    model = UserModel
    status_value = None  # устанавливается в подклассах
    template_name = None
    success_message = ''
    success_url = reverse_lazy('management:management', kwargs={'active_tab': 'users'})

    def get_object(self):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])

    def test_func(self):
        user = self.get_object()
        return self.request.user.is_staff and self.request.user != user

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'user_obj': self.get_object()})

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        user.status = self.status_value
        user.save(update_fields=['status'])

        messages.success(request, self.success_message.format(email=user.email))
        return redirect(self.success_url)


class UserDeactivateView(UserStatusMixin):
    status_value = 'not_active'
    template_name = 'management/users_modals/user_confirm_deactivate.html'
    success_message = _("Пользователь {email} был деактивирован.")


class UserActivateView(UserStatusMixin):
    status_value = 'active'
    template_name = 'management/users_modals/user_confirm_activate.html'
    success_message = _("Пользователь {email} был активирован.")


class AdminUserBookingsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Booking
    template_name = 'management/users_modals/user_bookings.html'
    context_object_name = 'bookings'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        self.user_profile = get_object_or_404(get_user_model(), pk=user_id)
        return Booking.objects.filter(user=self.user_profile).select_related(
            'table', 'promo_code', 'special_offer', 'pricing'
        ).prefetch_related('equipment').order_by('-start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = self.user_profile
        context['bookings_detailed'] = [self.format_booking(b) for b in context['bookings']]
        context['users'] = get_user_model().objects.all()

        return context

    def format_booking(self, b):
        return {
            'id': b.id,
            'start_date': localtime(b.start_time).strftime('%d.%m.%Y'),
            'start_time': localtime(b.start_time).strftime('%H:%M'),
            'end_time': localtime(b.end_time).strftime('%H:%M'),
            'table': str(b.table),
            'status': b.get_status_display(),
            'participants': b.participants,
            'is_group': b.is_group,
            'base_price': b.base_price,
            'equipment_price': b.equipment_price,
            'total_price': b.total_price,
            'promo_code': b.promo_code.code if b.promo_code else None,
            'special_offer': b.special_offer.name if b.special_offer else None,
            'equipment': [eq.name for eq in b.equipment.all()],
            'notes': b.notes,
            'created_at': localtime(b.created_at).strftime('%d.%m.%Y %H:%M'),
            'updated_at': localtime(b.updated_at).strftime('%d.%m.%Y %H:%M'),
            'expires_at': localtime(b.expires_at).strftime('%d.%m.%Y %H:%M'),
        }


@user_passes_test(lambda u: u.is_staff)
def loyalty_settings_view(request):
    # Получаем настройки
    settings = LoyaltySettings.load()

    # Получаем все уровни лояльности
    levels = LoyaltyProfile.Level.choices

    # Формируем данные для таблицы уровней
    loyalty_levels = []
    for level in levels:
        level_data = {
            'code': level[0],
            'name': level[1],
            'description': '',
            'threshold': LoyaltyProfile.LEVEL_THRESHOLDS.get(level[0], 0),
            'discount': LoyaltyProfile.LEVEL_DISCOUNTS.get(level[0], 0),
            'status': 'Активен',
            'icon': 'fa-star',
            'color': 'green'
        }

        # Настройки для каждого уровня
        if level[0] == 'SILVER':
            level_data['description'] = 'Средний уровень'
            level_data['icon'] = 'fa-award'
            level_data['color'] = 'gray'
        elif level[0] == 'GOLD':
            level_data['description'] = 'Продвинутый уровень'
            level_data['icon'] = 'fa-medal'
            level_data['color'] = 'yellow'
        elif level[0] == 'PLATINUM':
            level_data['description'] = 'Премиум уровень'
            level_data['icon'] = 'fa-crown'
            level_data['color'] = 'purple'
        else:
            level_data['description'] = 'Базовый уровень'

        loyalty_levels.append(level_data)

    # Получаем привилегии уровней
    level_benefits = {}
    for level in levels:
        benefits = LevelBenefit.objects.filter(level=level[0])
        level_benefits[level[0]] = {benefit.benefit_type: benefit.is_active for benefit in benefits}

    context = {
        'loyalty_levels': loyalty_levels,
        'points_settings': settings,
        'redemption_settings': settings,
        'level_benefits': level_benefits,
        'active_tab': 'loyalty_modals',
    }

    return render(request, 'management/management_templates/loyalty.html', context)

def add_level_benefit(request):
    if request.method == 'POST':
        form = LevelBenefitForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Привилегия успешно добавлена')
                return redirect('loyalty_program')  # Название URL вашей страницы с программой лояльности
            except Exception as e:
                form.add_error(None, f'Ошибка при сохранении: {e}')
    else:
        form = LevelBenefitForm()

    return render(request, 'management/loyalty_modals/add_level_benefit.html', {'form': form})


from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import PromoCode
from .serializers import PromoCodeSerializer

class PromoCodeViewSet(viewsets.ModelViewSet):
    queryset = PromoCode.objects.select_related('user').all()
    serializer_class = PromoCodeSerializer

