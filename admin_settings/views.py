from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from admin_settings.forms import TableForm, TableTypeForm, PricingPlanForm, TableTypePricingForm, SpecialOfferForm, \
    MembershipTypeForm, HolidayForm, ClubSettingsForm
from admin_settings.models import ClubSettings, SpecialOffer, MembershipType, Holiday
from bookings.models import Table, TableType, PricingPlan, TableTypePricing


class IsAdminMixin(UserPassesTestMixin):
    def __init__(self):
        self.request = None

    def test_func(self):
        return self.request.user.is_staff


class ClubSettingsView(LoginRequiredMixin, IsAdminMixin, View):
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
                'tables': Table.objects.all().select_related('table_type'),
                'table_types': TableType.objects.all(),
                'table_form': TableForm(),
                'table_type_form': TableTypeForm(),
            })
        elif active_tab == 'pricing':
            context.update({
                'pricing_plans': PricingPlan.objects.all(),
                'table_type_pricing': TableTypePricing.objects.all().select_related('table_type', 'pricing_plan'),
                'special_offers': SpecialOffer.objects.all(),
                'pricing_plan_form': PricingPlanForm(),
                'table_type_pricing_form': TableTypePricingForm(),
                'special_offer_form': SpecialOfferForm(),
            })
        elif active_tab == 'memberships':
            context.update({
                'membership_types': MembershipType.objects.all(),
                'membership_form': MembershipTypeForm(),
            })
        elif active_tab == 'schedule':
            context.update({
                'holidays': Holiday.objects.all(),
                'holiday_form': HolidayForm(),
            })
        elif active_tab == 'general':
            context['settings_form'] = ClubSettingsForm(instance=context['club_settings'])

        return context


# Таблицы
class TableCreateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        form = TableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Стол успешно добавлен")
        else:
            messages.error(request, "Ошибка при добавлении стола")
        return redirect('club_settings', active_tab='tables')


class TableUpdateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, pk, *args, **kwargs):
        table = get_object_or_404(Table, pk=pk)
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            messages.success(request, "Стол успешно обновлен")
        else:
            messages.error(request, "Ошибка при обновлении стола")
        return redirect('club_settings', active_tab='tables')


class TableDeleteView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, pk, *args, **kwargs):
        table = get_object_or_404(Table, pk=pk)
        table.delete()
        messages.success(request, "Стол успешно удален")
        return redirect('club_settings', active_tab='tables')


# Типы столов
class TableTypeCreateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        form = TableTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Тип стола успешно добавлен")
        else:
            messages.error(request, "Ошибка при добавлении типа стола")
        return redirect('club_settings', active_tab='tables')


# Цены
class PricingPlanCreateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        form = PricingPlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Тарифный план успешно добавлен")
        else:
            messages.error(request, "Ошибка при добавлении тарифного плана")
        return redirect('club_settings', active_tab='pricing')


class TableTypePricingCreateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        form = TableTypePricingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Цена для типа стола успешно добавлена")
        else:
            messages.error(request, "Ошибка при добавлении цены")
        return redirect('club_settings', active_tab='pricing')


class SpecialOfferCreateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        form = SpecialOfferForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Специальное предложение успешно добавлено")
        else:
            messages.error(request, "Ошибка при добавлении предложения")
        return redirect('club_settings', active_tab='pricing')


# Абонементы
class MembershipTypeCreateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        form = MembershipTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Тип абонемента успешно добавлен")
        else:
            messages.error(request, "Ошибка при добавлении абонемента")
        return redirect('club_settings', active_tab='memberships')


# Расписание
class HolidayCreateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        form = HolidayForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Праздничный день успешно добавлен")
        else:
            messages.error(request, "Ошибка при добавлении праздничного дня")
        return redirect('club_settings', active_tab='schedule')


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
        return redirect('club_settings', active_tab='general')


class UpdateWorkingHoursView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        form = WorkingHoursForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Рабочие часы успешно обновлены")
        else:
            messages.error(request, "Ошибка при обновлении рабочих часов")