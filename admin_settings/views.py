from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from admin_settings.forms import TableForm, TableTypeForm,  \
     HolidayForm, ClubSettingsForm, WorkingHoursForm
from admin_settings.models import ClubSettings, Holiday, WorkingDay, NotificationSettings, Table, TableType, Equipment
from bookings.models import  TableTypePricing
from management.forms import MembershipTypeForm, SpecialOfferForm
from management.models import MembershipType, SpecialOffer, MaxUnpaidBookings
from pricing.forms import PricingPlanForm, TableTypePricingForm
from pricing.models import PricingPlan


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
            'club_settings': ClubSettings.objects.first() or ClubSettings.objects.create(),
            'notifications': NotificationSettings.objects.first(),
            'settings_form': ClubSettingsForm
        }

        if active_tab == 'tables':

            context.update({
                'tables': Table.objects.all(),
                'table_form': TableForm(),
                'table_type_form': TableTypeForm(),  # Добавьте эту строку
                'table_types': TableType.objects.all(),

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



        elif active_tab == 'pricing':
            table_types = TableType.objects.all()
            pricing_plans = PricingPlan.objects.all()
            equipment_pricings= Equipment.objects.all()

            context.update({

                'table_types': table_types,
                'table_types_json': serializers.serialize('json', table_types),
                    'pricing_plans': pricing_plans,
                'pricing_plans_json': serializers.serialize('json', pricing_plans),

                'equipment_pricings': equipment_pricings,
                'max_unpaid_bookings': MaxUnpaidBookings.objects.first().max_unpaid_bookings,
                'pricing_plan_form': PricingPlanForm(),
                'table_type_pricing': TableTypePricing.objects.all(),
                'table_type_pricing_form': TableTypePricingForm(),
                'special_offers': SpecialOffer.objects.all(),
                'special_offer_form': SpecialOfferForm(),
                'tables': Table.objects.all(),
                'days_of_week': [
                    {'value': '1', 'label': 'Пн'},
                    {'value': '2', 'label': 'Вт'},
                    {'value': '3', 'label': 'Ср'},
                    {'value': '4', 'label': 'Чт'},
                    {'value': '5', 'label': 'Пт'},
                    {'value': '6', 'label': 'Сб'},
                    {'value': '7', 'label': 'Вс'}
                ],
                'default_weekdays': ['1', '2', '3', '4', '5', '6', '7']

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


class PricingPlanDetailView(LoginRequiredMixin, IsAdminMixin, View):
    def get(self, request, pk, *args, **kwargs):
        pricing_plan = get_object_or_404(PricingPlan, pk=pk)

        data = {
            'id': pricing_plan.id,
            'name': pricing_plan.name,
            'is_default': pricing_plan.is_default,
            'valid_from': pricing_plan.valid_from.strftime('%Y-%m-%d'),
            'valid_to': pricing_plan.valid_to.strftime('%Y-%m-%d') if pricing_plan.valid_to else None,
            'time_from': pricing_plan.time_from.strftime('%H:%M'),
            'time_to': pricing_plan.time_to.strftime('%H:%M'),
        }

        return JsonResponse(data)


class TableDetailView(LoginRequiredMixin, IsAdminMixin, View):
    def get(self, request, pk, *args, **kwargs):
        table = get_object_or_404(Table, pk=pk)
        data = {
            'id': table.id,
            'number': table.number,
            'table_type': {
                'id': table.table_type.id,
                'name': table.table_type.name
            },
            'description': table.description,
            'is_active': table.is_active
        }
        return JsonResponse(data)


class TableTypeView(LoginRequiredMixin, IsAdminMixin, View):
    def get(self, request, pk, *args, **kwargs):
        table_type = get_object_or_404(TableType, pk=pk)

        data = {
            'id': table_type.id,
            'description': table_type.description,
            'name': table_type.name,
            'max_capacity': table_type.max_capacity

        }

        return JsonResponse(data)


class TableTypeUpdateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, pk, *args, **kwargs):
        table_type = get_object_or_404(TableType, pk=pk)
        form = TableTypeForm(request.POST, instance=table_type)

        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Тип стола успешно обновлен'})

        return JsonResponse(
            {'status': 'error', 'message': 'Ошибка валидации', 'errors': form.errors},
            status=400
        )


class TableTypeDeleteView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, pk, *args, **kwargs):
        table_type = get_object_or_404(TableType, pk=pk)

        try:
            table_type.delete()
            return JsonResponse({'status': 'success', 'message': 'Тип стола успешно удален'})
        except Exception as e:
            return JsonResponse(
                {'status': 'error', 'message': str(e)},
                status=400
            )

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



import json


class HolidayView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        holiday = get_object_or_404(Holiday, pk=pk)

        data = {
            'id': holiday.id,
            'date': holiday.date.strftime('%d.%m.%Y'),
            'description': holiday.description,
            'status': holiday.get_status_display(),
            'open_time': holiday.open_time.strftime('%H:%M') if holiday.open_time else None,
            'close_time': holiday.close_time.strftime('%H:%M') if holiday.close_time else None
        }

        return JsonResponse(data)


class HolidayUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        try:
            holiday = get_object_or_404(Holiday, pk=pk)
            data = json.loads(request.body)
            form = HolidayForm(data, instance=holiday)

            if form.is_valid():
                updated_holiday = form.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Праздничный день обновлен',
                    'data': {
                        'id': updated_holiday.id,
                        'date': updated_holiday.date.strftime('%d.%m.%Y'),
                        'description': updated_holiday.description,
                        'status': updated_holiday.get_status_display(),
                        'open_time': updated_holiday.open_time.strftime('%H:%M') if updated_holiday.open_time else None,
                        'close_time': updated_holiday.close_time.strftime(
                            '%H:%M') if updated_holiday.close_time else None
                    }
                })

            return JsonResponse({
                'status': 'error',
                'message': 'Ошибка валидации',
                'errors': form.errors
            }, status=400)

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


class HolidayDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        try:
            holiday = get_object_or_404(Holiday, pk=pk)

            holiday.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'Праздничный день удален'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import logging
logger = logging.getLogger('tt')
# @login_required



@csrf_exempt
@require_http_methods(["POST"])
def create_equipment(request):
    try:
        data = json.loads(request.body)
        equipment = Equipment.objects.create(
            name=data.get('name'),
            description=data.get('description', ''),
            price_per_hour=data.get('price_per_hour', 200),
            price_per_half_hour=data.get('price_per_half_hour', 200),
            is_available=data.get('is_available', True)
        )
        return JsonResponse({
            'id': equipment.id,
            'name': equipment.name,
            'description': equipment.description,
            'price_per_hour': equipment.price_per_hour,
            'price_per_half_hour': equipment.price_per_half_hour,
            'is_available': equipment.is_available,
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def update_equipment(request, equip_id):
    try:
        data = json.loads(request.body)
        equipment = Equipment.objects.get(id=equip_id)
        equipment.name = data.get('name', equipment.name)
        equipment.description = data.get('description', equipment.description)
        equipment.price_per_hour = data.get('price_per_hour', equipment.price_per_hour)
        equipment.price_per_half_hour = data.get('price_per_half_hour', equipment.price_per_half_hour)
        equipment.is_available = data.get('is_available', equipment.is_available)
        equipment.save()

        return JsonResponse({
            'id': equipment.id,
            'name': equipment.name,
            'description': equipment.description,
            'price_per_hour': equipment.price_per_hour,
            'price_per_half_hour': equipment.price_per_half_hour,
            'is_available': equipment.is_available,
            'status': 'success'
        })
    except Equipment.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Equipment not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_equipment(request, equip_id):
    try:
        equipment = Equipment.objects.get(id=equip_id)
        equipment.delete()
        return JsonResponse({'status': 'success'})
    except Equipment.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Equipment not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_http_methods(["GET"])
def get_equipment(request, equip_id):
    try:
        equipment = Equipment.objects.get(id=equip_id)
        return JsonResponse({
            'id': equipment.id,
            'name': equipment.name,
            'description': equipment.description,
            'price_per_hour': equipment.price_per_hour,
            'price_per_half_hour': equipment.price_per_half_hour,
            'is_available': equipment.is_available,
            'status': 'success'
        })
    except Equipment.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Equipment not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
@csrf_exempt  # если не используете csrf_token в шаблоне, иначе уберите эту строку
def set_max_unpaid_bookings(request):
    try:
        value = int(request.POST.get('max_unpaid_bookings', 2))
        obj, created = MaxUnpaidBookings.objects.get_or_create(pk=1)
        obj.max_unpaid_bookings = value
        obj.save()
        return JsonResponse({'success': True, 'message': 'Настройка сохранена'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)




@require_GET
def get_max_unpaid_bookings(request):
    obj, created = MaxUnpaidBookings.objects.get_or_create(pk=1)
    return JsonResponse({'max_unpaid_bookings': obj.max_unpaid_bookings})