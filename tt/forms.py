from django.forms import ModelForm
from django import forms

from admin_settings.models import Table


from django import forms


class TableSettingsForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['number', 'table_description', 'price_per_hour', 'price_per_half_hour', 'is_active']
        labels = {
            'number': 'Номер стола',
            'table_description': 'Описание стола',
            'price_per_hour': 'Цена за час (руб)',
            'price_per_half_hour': 'Цена за 30 мин (руб)',
            'is_active': 'Активен'
        }
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
            'table_description': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
            'price_per_hour': forms.NumberInput(attrs={'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
            'price_per_half_hour': forms.NumberInput(attrs={'class': 'mt-1 block w-full rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'rounded border-2  border border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'}),
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
