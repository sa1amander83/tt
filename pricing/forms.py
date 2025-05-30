from django import forms

from pricing.models import PricingPlan, TableTypePricing


class PricingPlanForm(forms.ModelForm):
    class Meta:
        model = PricingPlan
        fields = ['name', 'description', 'is_default', 'valid_from', 'valid_to', 'time_from', 'time_to']
        labels = {
            'name': 'Название тарифа',
            'description': 'Описание',
            'is_default': 'Тариф по умолчанию',
            'valid_from': 'Действует с',
            'valid_to': 'Действует до',
            'time_from': 'Время начала',
            'time_to': 'Время окончания',}
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'mt-2 rounded border-2 border border-2 border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
            }),
            'valid_from': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'valid_to': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md  border-2 border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),

            'time_from': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'time_to': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),




        }


class TableTypePricingForm(forms.ModelForm):
    class Meta:
        model = TableTypePricing
        fields = ['table_type', 'pricing_plan', 'hour_rate', 'half_hour_rate', 'hour_rate_group', 'min_duration',
                  'max_duration']
        labels = {
            'table_type': 'Тип стола',
            'pricing_plan': 'Тарифный план',
            'hour_rate': 'Почасовая ставка',
            'half_hour_rate': 'Ставка за полчаса',
            'hour_rate_group': 'Групповая почасовая ставка',
            'min_duration': 'Минимальная продолжительность',
            'max_duration': 'Максимальная продолжительность',
        }
        widgets = {
            'table_type': forms.Select(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'pricing_plan': forms.Select(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'hour_rate': forms.NumberInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'half_hour_rate': forms.NumberInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'hour_rate_group': forms.NumberInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'min_duration': forms.NumberInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'max_duration': forms.NumberInput(attrs={'step': '30',
                                                     'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
                                                     }),
        }
