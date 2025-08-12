from django.utils.timezone import localtime

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, UpdateView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView

from bookings.models import Booking
from .forms import ProfileUpdateForm, PasswordChangeForm, ProfilePhotoForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from accounts.forms import SignUpForm, SignInForm


# Create your views here.
class SignUpView(View):
    """ User registration view """
    template_name = "accounts/register.html"
    form_class = SignUpForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            # You might want to add additional processing here
            return redirect("accounts:signin")
        context = {"form": form}
        return render(request, self.template_name, context)


class SignInView(View):
    template_name = "accounts/login.html"
    form_class = SignInForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            login_field = form.cleaned_data['login']
            password = form.cleaned_data['password']
            method = form.cleaned_data['login_method']

            # Аутентификация
            user = None
            if method == 'email':
                user = get_user_model().objects.filter(email__iexact=login_field).first()

            elif method == 'phone':
                user = get_user_model().objects.filter(phone=login_field).first()

            if user and user.check_password(password):
                login(request, user)
                return redirect("accounts:profile")
            else:
                form.add_error(None, "Неправильно введен логин или пароль")

        return render(request, self.template_name, {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:signin')

def restore_view(request):
    return render(request, "accounts/recover.html")


from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from .forms import ProfileUpdateForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

class CurrentUserView(APIView):
    # permission_classes = [IsAuthenticated]


    def get(self, request):
        user = request.user
        return Response({
            'isAuthenticated': True,
            'username': user.user_name,
            'user_id': user.id,
            'email': user.email,
            'phone': user.phone,

            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        })

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Основная информация профиля
        context['user'] = user
        context['profile_form'] = ProfileUpdateForm(instance=user)
        context['password_form'] = PasswordChangeForm(user=user)
        context['slot_view_mode'] = user.slot_view_mode or 30

        # Получаем бронирования пользователя, упорядоченные по дате начала (свежие первые)
        bookings_qs = Booking.objects.filter(user=user).order_by('-start_time')

        # Пагинация (опционально, можно убрать если не нужна)
        paginator = Paginator(bookings_qs, 10)  # по 10 бронирований на страницу
        page_number = self.request.GET.get('page', 1)
        bookings_page = paginator.get_page(page_number)

        # Преобразуем бронирования в удобный для шаблона формат с форматированными датами и статусом
        def format_booking(b):
            return {
                'id': b.id,
                'start_date': localtime(b.start_time).strftime('%d.%m.%Y'),
                'start_time': localtime(b.start_time).strftime('%H:%M'),
                'end_time': localtime(b.end_time).strftime('%H:%M'),
                'table': str(b.table),
                'status': b.get_status_display(),
                'status_key': b.status,
                'participants': b.participants,
                'is_group': b.is_group,
                'base_price': b.base_price,
                'equipment_price': b.equipment_price,
                'total_price': b.total_price,
                'promo_code': b.promo_code.code if b.promo_code else None,
                'promo_code_discount_percent': b.promo_code_discount_percent,
                'special_offer': b.special_offer.name if b.special_offer else None,
                'special_offer_discount_percent': b.special_offer_discount_percent,
                'equipment': [eq.name for eq in b.equipment.all()],
                'notes': b.notes,
                'created_at': localtime(b.created_at).strftime('%d.%m.%Y %H:%M'),
                'updated_at': localtime(b.updated_at).strftime('%d.%m.%Y %H:%M'),
                'expires_at': localtime(b.expires_at).strftime('%d.%m.%Y %H:%M'),
            }

        context['bookings'] = [format_booking(b) for b in bookings_page]
        context['bookings_page'] = bookings_page  # Для вывода пагинации в шаблоне
        # Данные программы лояльности
        context['loyalty_data'] = {
            'current_level': 'Старт',
            'current_points': 150,
            'points_to_next_level': 850,
            'progress_percent': 15,
            'next_level': 'Серебряный',
            'next_level_points': 1000,
            'current_discount': 0,
            'history': [
                {'date': '15.05.2023', 'description': 'Бронирование стола #1', 'points': 50},
                {'date': '10.05.2023', 'description': 'Бронирование стола #3', 'points': 40},
                {'date': '05.05.2023', 'description': 'Бронирование стола #2', 'points': 60},
            ]
        }

        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        context = self.get_context_data()

        if 'update_profile' in request.POST:
            profile_form = ProfileUpdateForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Профиль успешно обновлен')
                return redirect(reverse('accounts:profile') + '#profile-info')
            else:
                context['profile_form'] = profile_form

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Пароль успешно изменен')
                return redirect(reverse('accounts:profile') + '#password-change')
            else:
                context['password_form'] = password_form

        return self.render_to_response(context)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile.html'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'user_name': form.instance.user_name,
                'email': form.instance.email,
                'phone': form.instance.phone,
                'level': form.instance.level
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data()
            }, status=400)
        return super().form_invalid(form)


@login_required
@require_POST
def upload_profile_photo(request):
    user=get_user_model()
    form = ProfilePhotoForm(request.POST, request.FILES, instance=request.user)
    if form.is_valid():
        form.save()
        return JsonResponse({
            'success': True,
            'photo_url': request.user.photo.url if request.user.photo else None
        })
    return JsonResponse({
        'success': False,
        'errors': form.errors.get_json_data()
    }, status=400)


# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

import logging

logger = logging.getLogger(__name__)


@login_required
@require_POST
def update_slot_view_mode(request):
    try:
        data = json.loads(request.body)
        view_mode = int(data.get('slot_view_mode', 30))
        logger.info(f"Получен запрос на обновление режима: {view_mode} для пользователя {request.user}")

        if view_mode not in [30, 60]:
            raise ValueError("Invalid view mode")

        request.user.slot_view_mode = view_mode
        request.user.save()
        logger.info(f"Сохранено значение: {request.user.slot_view_mode}")

        return JsonResponse({
            'status': 'success',
            'refresh_required': True
        })
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)



from datetime import timedelta, date


def can_use_membership(user, booking_start, duration_minutes):
    membership = user.memberships.filter(
        is_active=True,
        start_date__lte=booking_start.date(),
        end_date__gte=booking_start.date()
    ).first()

    if not membership:
        return False, "Нет активного абонемента"

    mtype = membership.membership_type

    # Проверка дней недели
    if str(booking_start.isoweekday()) not in mtype.valid_days:
        return False, "Абонемент не действует в этот день"

    # Проверка времени
    if mtype.time_from and mtype.time_to:
        if not (mtype.time_from <= booking_start.time() <= mtype.time_to):
            return False, "Время не входит в доступное окно абонемента"

    # Проверка лимитов по часам
    if not mtype.is_unlimited:
        remaining_minutes = (mtype.included_hours * 60) - membership.used_minutes
        if duration_minutes > remaining_minutes:
            return False, f"Осталось только {remaining_minutes // 60} ч. {remaining_minutes % 60} мин."

    return True, "ОК"


def apply_membership_usage(user, duration_minutes):
    membership = user.memberships.filter(
        is_active=True,
        start_date__lte=date.today(),
        end_date__gte=date.today()
    ).first()

    if membership and not membership.membership_type.is_unlimited:
        membership.used_minutes += duration_minutes
        membership.save()


class StatisticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'management/management_templates/statistics.html'

    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавьте сюда любую статистику, которую хотите вывести
        # Например:
        from bookings.models import Booking
        from django.utils.timezone import now
        context['total_bookings'] = Booking.objects.count()
        context['completed_today'] = Booking.objects.filter(
            status='completed',
            start_time__date=now().date()
        ).count()
        return context
