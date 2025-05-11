from django.forms import ModelForm
from django import forms

from admin_settings.models import Tables
from events.models import Event, EventMember


class EventForm(ModelForm):
    table = forms.ModelChoiceField(
        queryset=Tables.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Event
        fields = ["title", "description", "start_time", "end_time", 'table', 'total_time', 'total_cost' ]
        # datetime-local is a HTML5 input type
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Описание"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Примечание или пожелание",
                    "rows": 3,
                }
            ),
            "start_time": forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'step': '1800',  # 30 минут в секундах
                    'min': '09:00',
                    'max': '23:00',
                    'class': 'form-control'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            "end_time": forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'step': '1800',
                    'min': '09:00',
                    'max': '23:00',
                    'class': 'form-control'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            "total_time": forms.NumberInput(
    attrs={
        'class': 'form-control',
        'min': '0',
        'step': '0.5',  # шаг в 0.5
        'max': '12',
        'placeholder': '0'
    }
)

        }
        exclude = ["user"]

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields["start_time"].input_formats = ("%Y-%m-%dT%H:%M",)
        self.fields["end_time"].input_formats = ("%Y-%m-%dT%H:%M",)


class AddMemberForm(forms.ModelForm):
    class Meta:
        model = EventMember
        fields = ["user"]




class TableSettingsForm(forms.ModelForm):
    class Meta:
        model = Tables
        fields = ['number', 'table_description', 'price_per_hour', 'price_per_half_hour','is_active']
        labels = {
            'number': 'Номер стола',
            'table_description': 'Описание стола',
            'price_per_hour': 'Цена за час (руб)',
            'price_per_half_hour': 'Цена за 30 мин (руб)',
            'is_active':'Активен'
        }
        widgets = {
            'table_description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        price_per_hour = cleaned_data.get('price_per_hour')
        price_per_half_hour = cleaned_data.get('price_per_half_hour')
        
        if price_per_hour and price_per_half_hour:
            if price_per_half_hour >= price_per_hour:
                raise forms.ValidationError("Цена за 30 минут должна быть меньше чем за час")
            if price_per_hour <= 0 or price_per_half_hour <= 0:
                raise forms.ValidationError("Цены должны быть положительными числами")
        
        return cleaned_data