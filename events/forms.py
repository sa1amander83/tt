from django import forms
from django.utils import timezone


from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_time', 'end_time', 'table', 'participants', 'notes']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500'
            }),
            'table': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500'
            }),
            'participants': forms.Select(
                choices=[(2, '2 участника'), (4, '4 участника')],
                attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500'}
            ),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500'
            }),
        }

    def clean_participants(self):
        participants = self.cleaned_data.get('participants')
        if participants < 1:
            raise forms.ValidationError("Количество участников должно быть не менее 1")
        if participants > 4:
            raise forms.ValidationError("Максимальное количество участников — 4")
        return participants

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError("Время начала должно быть раньше времени окончания")
            if start_time < timezone.now():
                raise forms.ValidationError("Нельзя бронировать в прошедшее время")

        return cleaned_data