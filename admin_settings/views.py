from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from admin_settings.forms import TableForm, TableTypeForm, PricingPlanForm, TableTypePricingForm, SpecialOfferForm, \
    MembershipTypeForm, HolidayForm, ClubSettingsForm, WorkingHoursForm
from admin_settings.models import ClubSettings, SpecialOffer, MembershipType, Holiday, WorkingDay
from bookings.models import Table, TableType, PricingPlan, TableTypePricing


class IsAdminMixin(UserPassesTestMixin):
    def __init__(self):
        self.request = None

    def test_func(self):
        return self.request.user.is_staff


class ClubSettingsView(LoginRequiredMixin, View):
    template_name = 'admin/admin-settings.html'

    def get(self, request, *args, **kwargs):
        active_tab = kwargs.get('active_tab', 'tables')
        context = self.get_context_data(active_tab)
        return render(request, self.template_name, context)

    def get_context_data(self, active_tab):
        context = {
            'active_tab': active_tab,
            'club_settings': ClubSettings.objects.first() or ClubSettings.objects.create()
        }

        if active_tab == 'tables':


            context.update({
                'tables': Table.objects.all(),
                'table_form': TableForm(),
                 'table_type_form': TableTypeForm(),  # Добавьте эту строку
                'table_types': TableType.objects.all(),

            })

        elif active_tab == 'memberships':
            context.update({
                'membership_types': MembershipType.objects.all(),
                'membership_form': MembershipTypeForm(),
            })

        elif active_tab == 'schedule':
            # Создаем недостающие дни недели
            if WorkingDay.objects.count() < 7:
                existing_days = set(WorkingDay.objects.values_list('day', flat=True))
                for day_int, day_name in WorkingDay.DAYS_OF_WEEK:
                    if day_int not in existing_days:
                        # Устанавливаем разное время для разных дней
                        if day_int == 4:  # Пятница
                            open_time = time(9, 0)
                            close_time = time(23, 0)
                        elif day_int == 5:  # Суббота
                            open_time = time(10, 0)
                            close_time = time(23, 0)
                        elif day_int == 6:  # Воскресенье
                            open_time = time(10, 0)
                            close_time = time(22, 0)
                        else:  # Будни
                            open_time = time(9, 0)
                            close_time = time(22, 0)

                        WorkingDay.objects.create(
                            day=day_int,
                            open_time=open_time,
                            close_time=close_time,
                            is_open=True
                        )

            working_days = WorkingDay.objects.all().order_by('day')
            holidays = Holiday.objects.all().order_by('-date')

            # Создаем формы для каждого дня
            working_hours_forms = []
            for day in working_days:
                form = WorkingHoursForm(instance=day, prefix=f'day_{day.day}')
                working_hours_forms.append((day, form))

            context.update({
                'working_hours_forms': working_hours_forms,
                'holidays': holidays,
                'holiday_form': HolidayForm(),
            })

        return context

    def post(self, request, *args, **kwargs):
        active_tab = kwargs.get('active_tab', 'tables')

        if active_tab == 'schedule':
            # Обработка рабочих часов
            working_days = WorkingDay.objects.all().order_by('day')
            for day in working_days:
                form = WorkingHoursForm(
                    request.POST,
                    instance=day,
                    prefix=f'day_{day.day}'
                )
                if form.is_valid():
                    form.save()
                else:
                    # Логирование ошибок для отладки
                    print(f"Ошибки в форме для дня {day.day}: {form.errors}")

            messages.success(request, "Часы работы обновлены")
            return redirect('admin_settings:club_settings', active_tab='schedule')


# Таблицы
class TableCreateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        form = TableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Стол успешно добавлен")
        else:
            messages.error(request, "Ошибка при добавлении стола")
        return redirect('admin_settings:club_settings', active_tab='tables')


class TableUpdateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, pk, *args, **kwargs):
        table = get_object_or_404(Table, pk=pk)
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            messages.success(request, "Стол успешно обновлен")
        else:
            messages.error(request, "Ошибка при обновлении стола")
        return redirect('admin_settings:club_settings', active_tab='tables')


class TableDeleteView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, pk, *args, **kwargs):
        table = get_object_or_404(Table, pk=pk)
        table.delete()
        messages.success(request, "Стол успешно удален")
        return redirect('admin_settings:club_settings', active_tab='tables')


# Типы столов
class TableTypeCreateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        form = TableTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Тип стола успешно добавлен")
        else:
            messages.error(request, "Ошибка при добавлении типа стола")
        return redirect('admin_settings:club_settings', active_tab='tables')


# Цены
class PricingPlanCreateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        form = PricingPlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Тарифный план успешно добавлен")
        else:
            messages.error(request, "Ошибка при добавлении тарифного плана")
        return redirect('admin_settings:club_settings', active_tab='pricing')


class TableTypePricingCreateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        form = TableTypePricingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Цена для типа стола успешно добавлена")
        else:
            messages.error(request, "Ошибка при добавлении цены")
        return redirect('admin_settings:club_settings', active_tab='pricing')


class SpecialOfferCreateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        form = SpecialOfferForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Специальное предложение успешно добавлено")
        else:
            messages.error(request, "Ошибка при добавлении предложения")
        return redirect('admin_settings:club_settings', active_tab='pricing')


# Абонементы
class MembershipTypeCreateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        form = MembershipTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Тип абонемента успешно добавлен")
        else:
            messages.error(request, "Ошибка при добавлении абонемента")
        return redirect('admin_settings:club_settings', active_tab='memberships')


# Расписание
class HolidayCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = HolidayForm(request.POST)
        if form.is_valid():
            holiday = form.save()
            messages.success(request, f"Праздничный день {holiday.date} добавлен")
            return redirect('admin_settings:club_settings', active_tab='schedule')

        # Если форма невалидна
        messages.error(request, "Ошибка при добавлении праздника")
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
        return redirect('admin_settings:club_settings', active_tab='schedule')


# Общие настройки
class ClubSettingsUpdateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        club_settings = ClubSettings.objects.first() or ClubSettings.objects.create()
        form = ClubSettingsForm(request.POST, instance=club_settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Настройки успешно обновлены")
        else:
            messages.error(request, "Ошибка при обновлении настроек")
        return redirect('admin_settings:club_settings', active_tab='general')


class UpdateWorkingHoursView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        working_days = WorkingDay.objects.all().order_by('day')
        all_valid = True

        for day in working_days:
            form = WorkingHoursForm(
                request.POST,
                instance=day,
                prefix=f'day_{day.day}',
                initial={'day': day.day}  # Устанавливаем начальное значение для day
            )
            if form.is_valid():
                form.save()
            else:
                all_valid = False
                print(f"Ошибки для дня {day.day}: {form.errors}")

        if all_valid:
            messages.success(request, "Часы работы успешно обновлены")
        else:
            messages.error(request, "Произошли ошибки при сохранении")

        return redirect('admin_settings:club_settings', active_tab='schedule')
from datetime import time



# class ScheduleSettingsView(View):
#     template_name = 'admin/schedule_settings.html'
#
#     def get_working_days(self):
#         """Получаем или создаем все дни недели"""
#         working_days = list(WorkingDay.objects.all().order_by('day'))
#
#         if len(working_days) < 7:
#             existing_days = {day.day for day in working_days}
#             default_hours = {
#                 0: (time(9, 0), time(22, 0), True),  # Понедельник
#                 1: (time(9, 0), time(22, 0), True),  # Вторник
#                 2: (time(9, 0), time(22, 0), True),  # Среда
#                 3: (time(9, 0), time(22, 0), True),  # Четверг
#                 4: (time(9, 0), time(23, 0), True),  # Пятница
#                 5: (time(10, 0), time(23, 0), True),  # Суббота
#                 6: (time(10, 0), time(22, 0), True),  # Воскресенье
#             }
#
#             for day_num in range(7):
#                 if day_num not in existing_days:
#                     open_time, close_time, is_open = default_hours[day_num]
#                     WorkingDay.objects.create(
#                         day=day_num,
#                         open_time=open_time,
#                         close_time=close_time,
#                         is_open=is_open
#                     )
#             # Обновляем список после создания
#             working_days = list(WorkingDay.objects.all().order_by('day'))
#
#         return working_days
#
#
#
#     def post(self, request):
#         # Обработка рабочих часов
#         working_days = self.get_working_days()
#         for day in working_days:
#             form = WorkingHoursForm(
#                 request.POST,
#                 instance=day,
#                 prefix=f'day_{day.day}'
#             )
#             if form.is_valid():
#                 form.save()
#
#         # Обработка праздничных дней
#         holiday_form = HolidayForm(request.POST)
#         if holiday_form.is_valid():
#             holiday_form.save()
#             messages.success(request, "Праздничный день добавлен")
#         else:
#             for error in holiday_form.errors.values():
#                 messages.error(request, error)
#
#         return redirect('admin_settings:schedule')