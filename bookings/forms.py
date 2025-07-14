from django import forms
from django.contrib.auth import get_user_model

from bookings.models import Booking
from admin_settings.models import Equipment
from management.models import PromoCode

User = get_user_model()
DURATION_CHOICES = [
    (30, '30 минут'),
    (60, '1 час'),
    (90, '1.5 часа'),
    (120, '2 часа'),
    (150, '2.5 часа'),
    (180, '3 часа'),
]


class BookingForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Пользователь",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-xl border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm'
        })
    )

    duration_minutes = forms.ChoiceField(
        choices=DURATION_CHOICES,
        label="Длительность",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-xl border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm'
        })
    )

    equipment = forms.ModelMultipleChoiceField(
        queryset=Equipment.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'rounded border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
        }),
        required=False,
        label="Оборудование"
    )

    status = forms.ChoiceField(
        choices=Booking.STATUS_CHOICES,
        label="Статус",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-xl border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm'
        })
    )

    promo_code = forms.ModelChoiceField(
        queryset=PromoCode.objects.all(),
        to_field_name='code',
        required=False,
        label="Промокод",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-xl border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm'
        })
    )

    class Meta:
        model = Booking
        fields = [
            'table', 'user', 'start_time', 'duration_minutes',
            'participants', 'is_group', 'notes',
            'status', 'promo_code'  # 👈 обязательно включить эти поля
        ]

    def clean_promo_code(self):
        return self.cleaned_data.get('promo_code') or None