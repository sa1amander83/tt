from django import forms

from admin_settings.models import Equipment
from bookings.models import  Booking


class BookingForm(forms.ModelForm):
    equipment = forms.ModelMultipleChoiceField(
        queryset=Equipment.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Booking
        fields = ['table', 'start_time', 'duration', 'participants', 'is_group', 'notes']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'duration': forms.Select(
                choices=[(.5, '30 минут'), (1, '1 час'), (1.5, '1.5 часа'), (2, '2 часа'), (2.5, '2.5 часа'),
                         (3, '3 часа')]),
        }
