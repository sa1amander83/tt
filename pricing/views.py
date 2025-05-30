from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import View

from admin_settings.views import IsAdminMixin
from pricing.forms import PricingPlanForm, TableTypePricingForm
from pricing.models import PricingPlan, TableTypePricing


# Create your views here.

# Цены
class PricingPlanCreateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        form = PricingPlanForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse(
                {'status': 'error', 'message': 'Проверьте введенные данные'},
                status=400
            )


class PricingPlanView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, pk, *args, **kwargs):
        try:
            pricing_plan = get_object_or_404(PricingPlan, pk=pk)
            data = {
                'id': pricing_plan.id,
                'name': pricing_plan.name,
                'description': pricing_plan.description,
                'valid_from': pricing_plan.valid_from.isoformat(),
                'valid_to': pricing_plan.valid_to.isoformat() if pricing_plan.valid_to else None,
                'is_default': pricing_plan.is_default,
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse(
                {'status': 'error', 'message': str(e)},
                status=500
            )


class PricingPlanUpdateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, pk, *args, **kwargs):
        pricing_plan = get_object_or_404(PricingPlan, pk=pk)
        form = PricingPlanForm(request.POST, instance=pricing_plan)

        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})

        # Возвращаем ошибки валидации
        return JsonResponse(
            {
                'status': 'error',
                'message': 'Validation error',
                'errors': dict(form.errors.items())
            },
            status=400
        )


class PricingPlanDeleteView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, pk, *args, **kwargs):
        pricing_plan = get_object_or_404(PricingPlan, pk=pk)

        try:
            pricing_plan.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse(
                {'status': 'error', 'message': str(e)},
                status=400)


class TableTypePricingCreateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        form = TableTypePricingForm(request.POST)

        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})

        # Возвращаем ошибки валидации
        return JsonResponse(
            {
                'status': 'error',
                'message': 'Validation error',
                'errors': dict(form.errors.items())
            },
            status=400
        )


class TableTypePricingView(LoginRequiredMixin, UserPassesTestMixin, View):
    """View для работы с ценами по типам столов"""

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, pk, *args, **kwargs):
        """Получение данных о ценообразовании для типа стола"""
        try:
            pricing = get_object_or_404(TableTypePricing, pk=pk)

            data = {
                'id': pricing.id,
                'table_type': {
                    'id': pricing.table_type.id,
                    'name': pricing.table_type.name,
                    'description': pricing.table_type.description
                },
                'pricing_plan': {
                    'id': pricing.pricing_plan.id,
                    'name': pricing.pricing_plan.name
                },
                'hour_rate': pricing.hour_rate,
                'half_hour_rate': pricing.half_hour_rate,
                'hour_rate_group': pricing.hour_rate_group,
                'min_duration': pricing.min_duration,
                'max_duration': pricing.max_duration,

            }

            return JsonResponse(data)

        except Exception as e:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Failed to get table type pricing details',
                    'error': str(e)
                },
                status=500)


class TableTypePricingUpdateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, pk, *args, **kwargs):
        table_type_pricing = get_object_or_404(TableTypePricing, pk=pk)
        form = TableTypePricingForm(request.POST, instance=table_type_pricing)

        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})

        return JsonResponse(
            {'status': 'error', 'message': 'Проверьте введенные данные', 'errors': form.errors},
            status=400
        )


class TableTypePricingDeleteView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, pk, *args, **kwargs):
        table_type_pricing = get_object_or_404(TableTypePricing, pk=pk)

        try:
            table_type_pricing.delete()
            return JsonResponse({'status': 'success', 'message': 'Успешно удалено'})
        except Exception as e:
            return JsonResponse(
                {'status': 'error', 'message': str(e)},
                status=400)


