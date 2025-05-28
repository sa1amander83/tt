from django import forms

from admin_settings.models import MembershipType, SpecialOffer, Holiday, ClubSettings, WorkingDay
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
                'class': 'mt-2 rounded border-2 border border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['table_type'].queryset = TableType.objects.all()


from django import forms
from admin_settings.models import MembershipType, SpecialOffer, Holiday, ClubSettings
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


from django import forms
from .models import MembershipType

class MembershipTypeForm(forms.ModelForm):
    class Meta:
        model = MembershipType
        fields = [
            'name', 'description', 'duration_days', 'price',
            'discount_percent', 'included_hours', 'is_active',
            'includes_booking', 'includes_discount',
            'includes_tournaments', 'includes_training',
            'is_group_plan', 'is_unlimited'
        ]
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'duration_days': 'Продолжительность (дни)',
            'price': 'Цена',
            'discount_percent': 'Процент скидки',
            'included_hours': 'Включено часов',
            'is_active': 'Активен',
            'includes_booking': 'Включает бронирование',
            'includes_discount': 'Включает скидки',
            'includes_tournaments': 'Включает турниры',
            'includes_training': 'Включает тренировки',
            'is_group_plan': 'Групповой план',
            'is_unlimited': 'Безлимитный',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'duration_days': forms.NumberInput(attrs={
                'class': 'w-full mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'min': 1
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'min': 0
            }),
            'discount_percent': forms.NumberInput(attrs={
                'class': 'w-full mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'min': 0,
                'max': 100
            }),
            'included_hours': forms.NumberInput(attrs={
                'class': 'w-full mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'min': 0
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
            'is_group_plan': forms.CheckboxInput(attrs={
                'class': 'mt-2 rounded border-2 border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
            }),
            'is_unlimited': forms.CheckboxInput(attrs={
                'class': 'mt-2 rounded border-2 border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
            }),
        }
        help_texts = {
            'included_hours': '0 означает неограниченное количество часов',
            'discount_percent': 'Процент скидки на дополнительные услуги (0-100)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values
        self.fields['duration_days'].initial = 30
        self.fields['discount_percent'].initial = 0
        self.fields['included_hours'].initial = 0
        self.fields['is_active'].initial = True
        self.fields['includes_booking'].initial = True

class SpecialOfferForm(forms.ModelForm):
    class Meta:
        model = SpecialOffer
        fields = ['name', 'description', 'discount_percent', 'is_active', 'valid_from', 'valid_to',
                  'apply_to_all', 'tables', 'time_from', 'time_to', 'weekdays']
        weekdays = forms.MultipleChoiceField(
            choices=[(str(i), label) for i, label in [
                (1, 'Пн'), (2, 'Вт'), (3, 'Ср'), (4, 'Чт'),
                (5, 'Пт'), (6, 'Сб'), (7, 'Вс')
            ]],
            widget=forms.CheckboxSelectMultiple,
            required=False
        )
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
                'class': 'mt-2 rounded border border-2 border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
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
                'class': 'mt-2 rounded border border-2 border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
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
            'weekdays': forms.CheckboxSelectMultiple(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        apply_to_all = cleaned_data.get('apply_to_all')
        tables = cleaned_data.get('tables')

        if not apply_to_all and not tables:
            raise forms.ValidationError("Необходимо выбрать столы или отметить 'Применять ко всем столам'")

        if apply_to_all and tables:
            cleaned_data['tables'] = []  # Очищаем выбранные столы если apply_to_all=True

        return cleaned_data

    def clean_weekdays(self):
        weekdays_list = self.cleaned_data.get('weekdays', [])
        return ','.join(weekdays_list)  # Преобразуем в строку: "1,3,5"
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
                'name': 'open_time',
                'type': 'time',
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'close_time': forms.TimeInput(attrs={
                'name': 'close_time',
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
                'class': 'w-full px-3 py-2 sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'club_description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full  px-3 py-2 sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),

            'club_email': forms.EmailInput(attrs={
                'type': 'email',
                'class': 'w-full px-3 py-2 sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),

            'club_phone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),

            'club_address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3 py-2 sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'currency': forms.Select(attrs={
                'class': 'w-full px-3 py-2 sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),

            'timezone': forms.Select(attrs={
                'class': 'w-full px-3 py-2 sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'date_format': forms.Select(attrs={
                'class': 'w-full px-3 py-2 sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'time_format': forms.Select(attrs={
                'class': 'w-full px-3 py-2 sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'notify_bookings': forms.CheckboxInput(attrs={
                'class': "h-4 w-4 text-green-600 border  focus:ring-green-500 border-gray-300 rounded"
            }),
            'notify_payments': forms.CheckboxInput(attrs={
                'class': "h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"}),
            'notify_cancellations': forms.CheckboxInput(attrs={
                'class': "h-4 w-4 text-green-600 focus:ring-green-500 border border-gray-300 rounded"}),
            'notify_registrations': forms.CheckboxInput(attrs={
                'class': "h-4 w-4 text-green-600 focus:ring-green-500 border border-gray-300 rounded"}),

            'auto_backup': forms.CheckboxInput(attrs={
                'class': "h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"}),
            'backup_frequency': forms.Select(attrs={
                'class': 'w-full px-3 py-2 sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm '
                'focus:border-indigo-500 focus:ring-indigo-500'}),
            'backup_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-3 py-2 sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm '
                'focus:border-indigo-500 focus:ring-indigo-500'}),

            'backup_retention': forms.Select(attrs={
                'class': 'w-full px-3 py-2 sm:w-1/2 mt-1 block rounded-md border-2 border-gray-300 shadow-sm '
                'focus:border-indigo-500 focus:ring-indigo-500'})
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
                'class': 'rounded border-2 border-gray-300 border  text-indigo-600 focus:ring-indigo-500'
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
