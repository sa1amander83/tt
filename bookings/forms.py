from django import forms
from django.contrib.auth import get_user_model

from bookings.models import Booking
from admin_settings.models import Equipment

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

    class Meta:
        model = Booking
        fields = ['table', 'user', 'start_time', 'duration_minutes', 'participants', 'is_group', 'notes']

        widgets = {
            'table': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-xl border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm'
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'mt-1 block w-full rounded-xl border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm'
            }),
            'participants': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-xl border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm',
                'min': 1
            }),
            'is_group': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-xl border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm',
                'rows': 3,
                'placeholder': 'Дополнительная информация...'
            }),
        }
