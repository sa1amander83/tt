from django import forms
from django.utils import timezone

from bookings.models import TimeSlot
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        # Убираем из формы поля, которые заполняются автоматически
        fields = ['timeslot', 'participants',  'notes']
        widgets = {
            'timeslot': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3 py-2 border border-2 border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500'
            }),
            'participants': forms.Select(
                choices=[(2, '2 участника'), (4, '4 участника')],
                attrs={'class': 'w-full px-3 py-2 border border-2 border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500'}
            ),
            'equipment_rental': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-green-600 focus:ring-green-500 border-2 border-gray-300 rounded'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Ограничиваем доступные слоты доступными и не прошедшими
            self.fields['timeslot'].queryset = TimeSlot.objects.filter(
                is_available=True,
                start_time__gte=timezone.now()
            )

    def clean_timeslot(self):
        timeslot = self.cleaned_data.get('timeslot')
        if not timeslot:
            raise forms.ValidationError("Выберите временной слот")
        if not timeslot.is_available:
            raise forms.ValidationError("Данный слот уже занят")
        if timeslot.start_time < timezone.now():
            raise forms.ValidationError("Невозможно забронировать прошедший слот")
        return timeslot

    def clean_participants(self):
        participants = self.cleaned_data.get('participants')
        if participants < 1:
            raise forms.ValidationError("Количество участников должно быть не менее 1")
        if participants > 4:
            raise forms.ValidationError("Максимальное количество участников - 4")
        return participants

    def clean(self):
        cleaned_data = super().clean()
        # Дополнительные проверки можно добавить здесь
        return cleaned_data
