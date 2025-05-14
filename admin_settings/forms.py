from django import forms

from admin_settings.models import MembershipType, SpecialOffer, Holiday, ClubSettings, SiteSettings, WorkingDay
from bookings.models import Table, TableType, PricingPlan, TableTypePricing



class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['number', 'table_type', 'description', 'is_active']
        labels = {
            'number': 'Номер стола',
            'table_type': 'Тип стола',
            'description': 'Дополнительное описание',
            'is_active': 'Активен',
        }
        widgets = {
            'number': forms.NumberInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'table_type': forms.Select(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'mt-2 rounded border-2 border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
            }),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['table_type'].queryset = TableType.objects.all()




from django import forms
from admin_settings.models import MembershipType, SpecialOffer, Holiday, ClubSettings, SiteSettings
from bookings.models import Table, TableType, PricingPlan, TableTypePricing

class TableTypeForm(forms.ModelForm):
    class Meta:
        model = TableType
        fields = ['name', 'description', 'default_capacity']
        labels = {
            'name': 'Название типа',
            'description': 'Описание',
            'default_capacity': 'Вместимость по умолчанию',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'default_capacity': forms.NumberInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md  border-2 border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
        }

class PricingPlanForm(forms.ModelForm):
    class Meta:
        model = PricingPlan
        fields = ['name', 'description', 'is_default', 'valid_from', 'valid_to']
        labels = {
            'name': 'Название тарифа',
            'description': 'Описание',
            'is_default': 'Тариф по умолчанию',
            'valid_from': 'Действует с',
            'valid_to': 'Действует до',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'mt-2 rounded border-2 border-2 border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
            }),
            'valid_from': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'valid_to': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md  border-2 border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
        }

class TableTypePricingForm(forms.ModelForm):
    class Meta:
        model = TableTypePricing
        fields = ['table_type', 'pricing_plan', 'hour_rate', 'hour_rate_group', 'min_duration', 'max_duration']
        labels = {
            'table_type': 'Тип стола',
            'pricing_plan': 'Тарифный план',
            'hour_rate': 'Почасовая ставка',
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
            'hour_rate_group': forms.NumberInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'min_duration': forms.NumberInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'max_duration': forms.NumberInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
        }

class MembershipTypeForm(forms.ModelForm):
    class Meta:
        model = MembershipType
        fields = ['name', 'description', 'duration_days', 'price', 'is_active',
                 'includes_booking', 'includes_discount', 'includes_tournaments', 'includes_training']
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'duration_days': 'Продолжительность (дни)',
            'price': 'Цена',
            'is_active': 'Активен',
            'includes_booking': 'Включает бронирование',
            'includes_discount': 'Включает скидки',
            'includes_tournaments': 'Включает турниры',
            'includes_training': 'Включает тренировки',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'duration_days': forms.NumberInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
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
        }

class SpecialOfferForm(forms.ModelForm):
    class Meta:
        model = SpecialOffer
        fields = ['name', 'description', 'discount_percent', 'is_active', 'valid_from', 'valid_to',
                 'apply_to_all', 'tables', 'time_from', 'time_to', 'weekdays']
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
                'class': 'mt-2 rounded border-2 border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
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
                'class': 'mt-2 rounded border-2 border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
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
            'weekdays': forms.SelectMultiple(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
        }

class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = ['date', 'description', 'status', 'open_time', 'close_time']
        labels = {
            'date': 'Дата',
            'description': 'Описание',
            'status': 'Статус',
            'open_time': 'Время открытия',
            'close_time': 'Время закрытия',
        }
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'open_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'close_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
        }

class ClubSettingsForm(forms.ModelForm):
    class Meta:
        model = ClubSettings
        fields = '__all__'
        widgets = {
            'club_name': forms.TextInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'club_description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'backup_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            # Add similar widgets for other fields as needed
        }

class WorkingHoursForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('day', None)

    class Meta:
        model = WorkingDay
        fields = ['is_open', 'open_time', 'close_time']

        widgets = {

            'day': forms.Select(attrs={
                'class': 'w-full rounded-md border-2 border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'is_open': forms.CheckboxInput(attrs={
                'class': 'rounded border-2 border-gray-300 text-indigo-600 focus:ring-indigo-500'
            }),
            'open_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full rounded-md border-2 border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'close_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full rounded-md border-2 border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
            }),
        }

    # def save(self, commit=True):
    #     instance = super().save(commit=False)
    #     instance.day = self.cleaned_data['day']  # Устанавливаем day из скрытого поля
    #     if commit:
    #         instance.save()
    #     return instance

class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = ['date', 'description', 'status', 'open_time', 'close_time']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full rounded-md border-2 border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'description': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-2 border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full rounded-md border-2 border-gray-300 focus:border-indigo-500 focus:ring-indigo-500',
                'onchange': 'toggleHolidayHours(this)'
            }),
            'open_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full rounded-md border-2 border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 holiday-hours'
            }),
            'close_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full rounded-md border-2 border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 holiday-hours'
            }),
        }
