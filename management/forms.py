from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from management.models import MembershipType, SpecialOffer, LevelBenefit, LoyaltyProfile


class UserAdminForm(UserChangeForm):
    password = forms.CharField(
        label="Пароль",
        strip=False,
        required=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'mt-1 block w-full rounded-md border border-green-400 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 sm:text-2xl'
        }),
        help_text="Оставьте пустым, если не хотите менять пароль. Минимум 8 символов."
    )

    class Meta:
        model = get_user_model()
        fields = [
            'email',
            'user_name',
            'phone',
            'role',
            'status',
            'password'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'mt-1 block w-full rounded-md border border-green-400 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 sm:text-xl'
            }),
            'user_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border border-green-400 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 sm:text-xl'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border border-green-400 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 sm:text-xl'
            }),
            'role': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border border-green-400 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 sm:text-xl'
            }),
            'status': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border border-green-400 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 sm:text-xl'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].required = False
        if self.instance.pk:
            # Для существующего пользователя:
            self.fields['email'].disabled = True
            self.fields['password'].help_text = (
                "Введите новый пароль, если хотите его изменить. "
                "Оставьте поле пустым, чтобы сохранить текущий пароль."
            )
        else:
            # Для нового пользователя:
            self.fields['password'].required = True
            self.fields['password'].help_text = "Минимум 8 символов."

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.instance.pk and not password:
            raise ValidationError("Для нового пользователя необходимо указать пароль.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')

        if password:
            user.set_password(password)

        if commit:
            user.save()
            self.save_m2m()

        return user


class UserAdminCreateForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = [
            'email',
            'user_name',
            'phone',
            'role',
            'status',
            'password1',
            'password2',

        ]
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'mt-1 block w-full rounded-md border border-green-400 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 sm:text-2xl'
            }),
            'user_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border border-green-400 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 sm:text-2xl'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border border-green-400 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 sm:text-2xl'
            }),
            'role': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border border-green-400 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 sm:text-2xl'
            }),
            'status': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border border-green-400 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 sm:text-2xl'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Обновляем виджеты для password полей
        self.fields['password1'].widget.attrs.update({
            'class': 'mt-1 block w-full rounded-md border border-green-400 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 sm:text-2xl'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'mt-1 block w-full rounded-md border border-green-400 shadow-sm focus:border-indigo-600 focus:ring-indigo-600 sm:text-2xl'
        })

class MembershipTypeForm(forms.ModelForm):
    class Meta:
        model = MembershipType
        fields = [
            'name', 'description', 'duration_days', 'price',
            'discount_percent', 'included_hours', 'is_active',
            'includes_booking', 'includes_discount',
            'includes_tournaments', 'includes_training',
            'is_group_plan', 'is_unlimited'
        ]
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'duration_days': 'Продолжительность (дни)',
            'price': 'Цена',
            'discount_percent': 'Процент скидки',
            'included_hours': 'Включено часов',
            'is_active': 'Активен',
            'includes_booking': 'Включает бронирование',
            'includes_discount': 'Включает скидки',
            'includes_tournaments': 'Включает турниры',
            'includes_training': 'Включает тренировки',
            'is_group_plan': 'Групповой план',
            'is_unlimited': 'Безлимитный',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'duration_days': forms.NumberInput(attrs={
                'class': 'w-full mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'min': 1
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'min': 0
            }),
            'discount_percent': forms.NumberInput(attrs={
                'class': 'w-full mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'min': 0,
                'max': 100
            }),
            'included_hours': forms.NumberInput(attrs={
                'class': 'w-full mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'min': 0
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'mt-2 rounded border-2 border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
            }),
            'includes_booking': forms.CheckboxInput(attrs={
                'class': 'mt-2 rounded border-2 border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
            }),
            'includes_discount': forms.CheckboxInput(attrs={
                'class': 'mt-2 rounded border-2 border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
            }),
            'includes_tournaments': forms.CheckboxInput(attrs={
                'class': 'mt-2 rounded border-2 border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
            }),
            'includes_training': forms.CheckboxInput(attrs={
                'class': 'mt-2 rounded border-2 border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
            }),
            'is_group_plan': forms.CheckboxInput(attrs={
                'class': 'mt-2 rounded border-2 border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
            }),
            'is_unlimited': forms.CheckboxInput(attrs={
                'class': 'mt-2 rounded border-2 border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
            }),
        }
        help_texts = {
            'included_hours': '0 означает неограниченное количество часов',
            'discount_percent': 'Процент скидки на дополнительные услуги (0-100)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values
        self.fields['duration_days'].initial = 30
        self.fields['discount_percent'].initial = 0
        self.fields['included_hours'].initial = 0
        self.fields['is_active'].initial = True
        self.fields['includes_booking'].initial = True

class SpecialOfferForm(forms.ModelForm):
    class Meta:
        model = SpecialOffer
        fields = ['name', 'description', 'discount_percent', 'is_active', 'valid_from', 'valid_to',
                  'apply_to_all', 'tables', 'time_from', 'time_to', 'weekdays']
        weekdays = forms.MultipleChoiceField(
            choices=[(str(i), label) for i, label in [
                (1, 'Пн'), (2, 'Вт'), (3, 'Ср'), (4, 'Чт'),
                (5, 'Пт'), (6, 'Сб'), (7, 'Вс')
            ]],
            widget=forms.CheckboxSelectMultiple,
            required=False
        )
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'discount_percent': 'Процент скидки',
            'is_active': 'Активна',
            'valid_from': 'Действует с',
            'valid_to': 'Действует до',
            'apply_to_all': 'Применять ко всем столам',
            'tables': 'Столы',
            'time_from': 'Время начала',
            'time_to': 'Время окончания',
            'weekdays': 'Дни недели',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'discount_percent': forms.NumberInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'mt-2 rounded border border-2 border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
            }),
            'valid_from': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'valid_to': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'apply_to_all': forms.CheckboxInput(attrs={
                'class': 'mt-2 rounded border border-2 border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
            }),
            'tables': forms.SelectMultiple(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'time_from': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'time_to': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'weekdays': forms.CheckboxSelectMultiple(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        apply_to_all = cleaned_data.get('apply_to_all')
        tables = cleaned_data.get('tables')

        if not apply_to_all and not tables:
            raise forms.ValidationError("Необходимо выбрать столы или отметить 'Применять ко всем столам'")

        if apply_to_all and tables:
            cleaned_data['tables'] = []  # Очищаем выбранные столы если apply_to_all=True

        return cleaned_data

    def clean_weekdays(self):
        weekdays_list = self.cleaned_data.get('weekdays', [])
        return ','.join(weekdays_list)  # Преобразуем в строку: "1,3,5"



class LevelBenefitForm(forms.ModelForm):
    class Meta:
        model = LevelBenefit
        fields = ['level', 'benefit_type', 'is_active', 'value', 'description']
        widgets = {
            'level': forms.Select(choices=LoyaltyProfile.Level.choices, attrs={'class': 'form-select'}),
            'benefit_type': forms.Select(choices=LevelBenefit.BENEFIT_TYPES, attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'value': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }