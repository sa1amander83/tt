import json
from datetime import date, datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import View, TemplateView
from rest_framework import serializers

from admin_settings.views import IsAdminMixin
from management.forms import MembershipTypeForm, SpecialOfferForm
from management.models import  SpecialOffer, MembershipType, PromoCode

User=get_user_model()
# Create your views here.
class SpecialOfferCreateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        form = SpecialOfferForm(request.POST)
        if form.is_valid():
            special_offer = form.save(commit=False)
            special_offer.save()
            form.save_m2m()
            return JsonResponse({'status': 'success'})

        return JsonResponse(
            {'status': 'error', 'message': 'Проверьте введенные данные', 'errors': form.errors},
            status=400
        )


class SpecialOfferView(LoginRequiredMixin, UserPassesTestMixin, View):
    """View для работы со специальными предложениями"""

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, pk, *args, **kwargs):
        """Получение данных специального предложения"""
        try:
            offer = get_object_or_404(
                SpecialOffer.objects.prefetch_related('tables'),
                pk=pk
            )

            data = {
                'id': offer.id,
                'name': offer.name,
                'description': offer.description,
                'discount_percent': offer.discount_percent,
                'valid_from': offer.valid_from.isoformat(),
                'valid_to': offer.valid_to.isoformat() if offer.valid_to else None,
                'is_active': offer.is_active,
                'apply_to_all': offer.apply_to_all,
                'weekdays': offer.weekdays,  # Оставляем как строку "1,2,3"
                'time_from': offer.time_from.strftime('%H:%M') if offer.time_from else None,
                'time_to': offer.time_to.strftime('%H:%M') if offer.time_to else None,
                'tables': [
                    {
                        'id': table.id,
                        'name': str(table),  # Используем __str__ модели Table
                        'table_type': table.table_type.name if table.table_type else None
                    }
                    for table in offer.tables.all()
                ] if not offer.apply_to_all else [],
            }

            return JsonResponse({'status': 'success', 'data': data})

        except Exception as e:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Failed to get special offer details',
                    'error': str(e)
                },
                status=500
            )

class SpecialOfferUpdateView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, pk, *args, **kwargs):
        offer = get_object_or_404(SpecialOffer, pk=pk)
        form = SpecialOfferForm(request.POST, instance=offer)

        if form.is_valid():
            updated_offer = form.save(commit=False)
            updated_offer.save()
            form.save_m2m()  # Критически важно для сохранения m2m
            return JsonResponse({'status': 'success'})

        return JsonResponse({'errors': form.errors}, status=400)


class SpecialOfferDeleteView(LoginRequiredMixin, IsAdminMixin, View):
    def post(self, request, pk, *args, **kwargs):
        special_offer = get_object_or_404(SpecialOffer, pk=pk)

        try:
            special_offer.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse(
                {'status': 'error', 'message': str(e)},
                status=400)


# Абонементы

class MembershipCreateView(LoginRequiredMixin,IsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        form = MembershipTypeForm(request.POST)
        if form.is_valid():
            membership = form.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Абонемент успешно создан',
                'data': {
                    'id': membership.id,
                    'name': membership.name
                }
            })

        return JsonResponse(
            {'status': 'error', 'message': 'Проверьте введенные данные', 'errors': form.errors},
            status=400
        )


class MembershipView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        membership = get_object_or_404(MembershipType, pk=pk)

        data = {
            'id': membership.id,
            'name': membership.name,
            'description': membership.description,
            'duration_days': membership.duration_days,
            'price': membership.price,
            'discount_percent': membership.discount_percent,
            'included_hours': membership.included_hours,
            'is_active': membership.is_active,
            'includes_booking': membership.includes_booking,
            'includes_discount': membership.includes_discount,
            'includes_tournaments': membership.includes_tournaments,
            'includes_training': membership.includes_training,
            'is_group_plan': membership.is_group_plan,
            'is_unlimited': membership.is_unlimited,
        }

        return JsonResponse(data)


class MembershipUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        try:
            membership = get_object_or_404(MembershipType, pk=pk)
            form = MembershipTypeForm(request.POST, instance=membership)

            if form.is_valid():
                membership = form.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Абонемент обновлен',
                    'data': {
                        'id': membership.id,
                        'name': membership.name
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


class MembershipDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        try:
            membership = get_object_or_404(MembershipType, pk=pk)
            membership_name = membership.name
            membership.delete()
            return JsonResponse({
                'status': 'success',
                'message': f'Абонемент "{membership_name}" успешно удален!'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
# views.py



@csrf_exempt  # Только для теста, лучше использовать csrf_token
@require_http_methods(["POST"])
def create_promocode(request):
    try:
        data = json.loads(request.body)

        code = data.get('code')
        discount = data.get('discount_percent')
        valid_from = data.get('valid_from')
        valid_to = data.get('valid_to')
        is_active = data.get('is_active', True)
        usage_limit = data.get('usage_limit')
        description = data.get('description', '')
        user_id = data.get('user')

        promocode = PromoCode(
            code=code,
            discount_percent=discount,
            valid_from=valid_from,
            valid_to=valid_to,
            is_active=is_active,
            usage_limit=usage_limit if usage_limit is not None else None,
            description=description
        )

        if user_id:
            try:
                promocode.user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=400)

        promocode.save()
        return JsonResponse({'success': True, 'id': promocode.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def promocode_detail(request, promo_id=None):
    if request.method == "GET":
        promo = get_object_or_404(PromoCode, id=promo_id)
        return JsonResponse({
            "id": promo.id,
            "code": promo.code,
            "description": promo.description,
            "discount_percent": promo.discount_percent,
            "valid_from": promo.valid_from.isoformat(),
            "valid_to": promo.valid_to.isoformat(),
            "is_active": promo.is_active,
            "usage_limit": promo.usage_limit,
            "used_count": promo.used_count,
            "user": promo.user.id if promo.user else None
        })

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if request.method == "POST":
        try:
            promo = PromoCode(
                code=data["code"],
                description=data.get("description", ""),
                discount_percent=int(data["discount_percent"]),
                valid_from=datetime.strptime(data["valid_from"], "%Y-%m-%d").date(),
                valid_to=datetime.strptime(data["valid_to"], "%Y-%m-%d").date(),
                is_active=data.get("is_active", True),
                usage_limit=data.get("usage_limit") or None,
                user=get_user_model()   .objects.get(id=data["user"]) if data.get("user") else None
            )
            promo.save()
            return JsonResponse({"id": promo.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    if request.method == "PUT":
        promo = get_object_or_404(PromoCode, id=promo_id)
        promo.code = data["code"]
        promo.description = data.get("description", "")
        promo.discount_percent = int(data["discount_percent"])
        promo.valid_from = datetime.strptime(data["valid_from"], "%Y-%m-%d").date()
        promo.valid_to = datetime.strptime(data["valid_to"], "%Y-%m-%d").date()
        promo.is_active = data.get("is_active", True)
        promo.usage_limit = data.get("usage_limit") or None
        promo.user = User.objects.get(id=data["user"]) if data.get("user") else None
        promo.save()
        return JsonResponse({"id": promo.id})

    if request.method == "DELETE":
        promo = get_object_or_404(PromoCode, id=promo_id)
        promo.delete()
        return JsonResponse({"deleted": True})

    return HttpResponseNotAllowed(['GET', 'POST', 'PUT', 'DELETE'])

class PromoCodeManagementView(LoginRequiredMixin, TemplateView):
    template_name = 'admin/promo_codes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['promocodes'] = PromoCode.objects.all().order_by('-valid_to')
        context['users'] = User.objects.filter(is_active=True).order_by('last_name')
        context['today'] = date.today()
        return context


# class PromoCodeListCreate(LoginRequiredMixin, View):
#     def get(self, request):
#         promocodes = PromoCode.objects.all().order_by('-valid_to')
#         data = [{
#             'id': pc.id,
#             'code': pc.code,
#             'description': pc.description,
#             'discount_percent': pc.discount_percent,
#             'valid_from': pc.valid_from.strftime('%Y-%m-%d'),
#             'valid_to': pc.valid_to.strftime('%Y-%m-%d'),
#             'is_active': pc.is_active,
#             'usage_limit': pc.usage_limit,
#             'used_count': pc.used_count,
#             'user': pc.user.id if pc.user else None
#         } for pc in promocodes]
#         return JsonResponse(data, safe=False)
#
#     def post(self, request):
#         try:
#             data = json.loads(request.body)
#
#             # Валидация
#             required_fields = ['code', 'discount_percent', 'valid_from', 'valid_to']
#             missing = [field for field in required_fields if field not in data]
#             if missing:
#                 return JsonResponse({'error': f'Missing required fields: {", ".join(missing)}'}, status=400)
#
#             if data['valid_from'] > data['valid_to']:
#                 return JsonResponse({'error': 'End date must be after start date'}, status=400)
#
#             if int(data['discount_percent']) <= 0 or int(data['discount_percent']) > 100:
#                 return JsonResponse({'error': 'Discount must be between 1 and 100 percent'}, status=400)
#
#             # Создание промокода
#             promo_code = PromoCode(
#                 code=data['code'].strip().upper(),
#                 description=data.get('description', ''),
#                 discount_percent=data['discount_percent'],
#                 valid_from=data['valid_from'],
#                 valid_to=data['valid_to'],
#                 is_active=data.get('is_active', True),
#                 usage_limit=data.get('usage_limit'),
#                 user_id=data.get('user')
#             )
#
#             promo_code.full_clean()
#             promo_code.save()
#
#             return JsonResponse({
#                 'success': True,
#                 'id': promo_code.id,
#                 'code': promo_code.code
#             })
#
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON'}, status=400)
#         except ValidationError as e:
#             return JsonResponse({'error': str(e)}, status=400)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)


class PromoCodeDetail(LoginRequiredMixin, View):
    def get(self, request, pk):
        try:
            pc = PromoCode.objects.get(pk=pk)
            data = {
                'id': pc.id,
                'code': pc.code,
                'description': pc.description,
                'discount_percent': pc.discount_percent,
                'valid_from': pc.valid_from.strftime('%Y-%m-%d'),
                'valid_to': pc.valid_to.strftime('%Y-%m-%d'),
                'is_active': pc.is_active,
                'usage_limit': pc.usage_limit,
                'used_count': pc.used_count,
                'user': pc.user.id if pc.user else None
            }
            return JsonResponse(data)
        except PromoCode.DoesNotExist:
            return JsonResponse({'error': 'Promo code not found'}, status=404)

    def put(self, request, pk):
        try:
            pc = PromoCode.objects.get(pk=pk)
            data = json.loads(request.body)

            # Validation
            if 'valid_from' in data and 'valid_to' in data and data['valid_from'] > data['valid_to']:
                return JsonResponse({'error': 'End date must be after start date'}, status=400)

            if 'discount_percent' in data and (
                    int(data['discount_percent']) <= 0 or int(data['discount_percent']) > 100):
                return JsonResponse({'error': 'Discount must be between 1 and 100 percent'}, status=400)

            # Update fields
            for field in ['code', 'description', 'discount_percent', 'valid_from', 'valid_to',
                          'is_active', 'usage_limit', 'user']:
                if field in data:
                    setattr(pc, field, data[field] if data[field] != '' else None)

            pc.full_clean()
            pc.save()

            return JsonResponse({'success': True, 'id': pc.id, 'code': pc.code})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except PromoCode.DoesNotExist:
            return JsonResponse({'error': 'Promo code not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def delete(self, request, pk):
        try:
            pc = PromoCode.objects.get(pk=pk)
            pc.delete()
            return JsonResponse({'success': True})
        except PromoCode.DoesNotExist:
            return JsonResponse({'error': 'Promo code not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
class PromoCodeRetrieveUpdateDestroy(LoginRequiredMixin, View):
    def get_object(self, pk):
        try:
            return PromoCode.objects.get(pk=pk)
        except PromoCode.DoesNotExist:
            return None

    def get(self, request, pk):
        promo_code = self.get_object(pk)
        if not promo_code:
            return JsonResponse({'error': 'Promo code not found'}, status=404)

        data = {
            'id': promo_code.id,
            'code': promo_code.code,
            'description': promo_code.description,
            'discount_percent': promo_code.discount_percent,
            'valid_from': promo_code.valid_from.strftime('%Y-%m-%d'),
            'valid_to': promo_code.valid_to.strftime('%Y-%m-%d'),
            'is_active': promo_code.is_active,
            'usage_limit': promo_code.usage_limit,
            'used_count': promo_code.used_count,
            'user': promo_code.user.id if promo_code.user else None
        }
        return JsonResponse(data)

    def put(self, request, pk):
        promo_code = self.get_object(pk)
        if not promo_code:
            return JsonResponse({'error': 'Promo code not found'}, status=404)

        try:
            data = json.loads(request.body)

            # Валидация
            if 'valid_from' in data and 'valid_to' in data and data['valid_from'] > data['valid_to']:
                return JsonResponse({'error': 'End date must be after start date'}, status=400)

            if 'discount_percent' in data and (
                    int(data['discount_percent']) <= 0 or int(data['discount_percent']) > 100):
                return JsonResponse({'error': 'Discount must be between 1 and 100 percent'}, status=400)

            # Обновление полей
            fields_to_update = [
                'code', 'description', 'discount_percent',
                'valid_from', 'valid_to', 'is_active', 'usage_limit', 'user'
            ]

            with transaction.atomic():
                for field in fields_to_update:
                    if field in data:
                        if field == 'user':
                            setattr(promo_code, field, User.objects.get(pk=data[field]) if data[field] else None)
                        else:
                            setattr(promo_code, field, data[field])

                promo_code.full_clean()
                promo_code.save()

            return JsonResponse({
                'success': True,
                'id': promo_code.id,
                'code': promo_code.code
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def delete(self, request, pk):
        promo_code = self.get_object(pk)
        if not promo_code:
            return JsonResponse({'error': 'Promo code not found'}, status=404)

        try:
            promo_code.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class ValidatePromoCode(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            code = data.get('code')
            user_id = data.get('user_id')

            if not code:
                return JsonResponse({'error': 'Promo code is required'}, status=400)

            try:
                promo = PromoCode.objects.get(code=code.upper())
            except PromoCode.DoesNotExist:
                return JsonResponse({'valid': False, 'error': 'Invalid promo code'})

            user = None
            if user_id:
                try:
                    user = User.objects.get(pk=user_id)
                except User.DoesNotExist:
                    pass

            is_valid = promo.is_valid_for_user(user) if user else promo.is_active

            if not is_valid:
                return JsonResponse({
                    'valid': False,
                    'error': 'This promo code is not valid for your account'
                })

            return JsonResponse({
                'valid': True,
                'discount_percent': promo.discount_percent,
                'code': promo.code,
                'description': promo.description
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)