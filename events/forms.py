from django import forms

from bookings.models import Tables, Booking

from django.utils import timezone


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['table', 'timeslot', 'participants', 'notes']
        widgets = {
            'timeslot': forms.HiddenInput(),
            'table': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'participants': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['table'].queryset = Tables.objects.available_for_user(user)

    def clean(self):
        data = super().clean()
        timeslot = data.get('timeslot')

        if timeslot and not timeslot.is_available:
            raise forms.ValidationError("Данный слот уже занят")

        if timeslot and timeslot.start_time < timezone.now():
            raise forms.ValidationError("Невозможно забронировать прошедший слот")

        return data