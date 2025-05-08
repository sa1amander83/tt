from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, UpdateView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
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


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Основная информация профиля
        context['user'] = user
        context['profile_form'] = ProfileUpdateForm(instance=user)
        context['password_form'] = PasswordChangeForm(user=user)

        # Пример данных для бронирований (замените на реальные данные из вашей модели)
        context['bookings'] = [
            {
                'date': '15.05.2023',
                'time': '18:00 - 19:00',
                'table': 'Стол #3',
                'status': 'Подтверждено',
                'status_class': 'bg-green-100 text-green-800'
            },
            {
                'date': '17.05.2023',
                'time': '19:00 - 20:00',
                'table': 'Стол #5',
                'status': 'Ожидание',
                'status_class': 'bg-yellow-100 text-yellow-800'
            }
        ]

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
                'email': form.instance.email
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