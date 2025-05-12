from django import forms

from admin_settings.models import MembershipType, SpecialOffer, Holiday, ClubSettings, SiteSettings
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
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'table_type': forms.Select(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'mt-2 rounded border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500'
            }),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['table_type'].queryset = TableType.objects.all()









class TableTypeForm(forms.ModelForm):
    class Meta:
        model = TableType
        fields = ['name', 'description', 'default_capacity']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class PricingPlanForm(forms.ModelForm):
    class Meta:
        model = PricingPlan
        fields = ['name', 'description', 'is_default', 'valid_from', 'valid_to']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'valid_from': forms.DateInput(attrs={'type': 'date'}),
            'valid_to': forms.DateInput(attrs={'type': 'date'}),
        }

class TableTypePricingForm(forms.ModelForm):
    class Meta:
        model = TableTypePricing
        fields = ['table_type', 'pricing_plan', 'hour_rate', 'hour_rate_group', 'min_duration', 'max_duration']

class MembershipTypeForm(forms.ModelForm):
    class Meta:
        model = MembershipType
        fields = ['name', 'description', 'duration_days', 'price', 'is_active',
                 'includes_booking', 'includes_discount', 'includes_tournaments', 'includes_training']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class SpecialOfferForm(forms.ModelForm):
    class Meta:
        model = SpecialOffer
        fields = ['name', 'description', 'discount_percent', 'is_active', 'valid_from', 'valid_to',
                 'apply_to_all', 'tables', 'time_from', 'time_to', 'weekdays']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'valid_from': forms.DateInput(attrs={'type': 'date'}),
            'valid_to': forms.DateInput(attrs={'type': 'date'}),
            'time_from': forms.TimeInput(attrs={'type': 'time'}),
            'time_to': forms.TimeInput(attrs={'type': 'time'}),
        }

class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = ['date', 'description', 'status', 'open_time', 'close_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'open_time': forms.TimeInput(attrs={'type': 'time'}),
            'close_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class ClubSettingsForm(forms.ModelForm):
    class Meta:
        model = ClubSettings
        fields = '__all__'
        widgets = {
            'club_description': forms.Textarea(attrs={'rows': 3}),
            'backup_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class WorkingHoursForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = ('opening_time', 'closing_time', 'slot_duration_minutes', 'weekend_days')

    pricing_plan = forms.ModelChoiceField(queryset=PricingPlan.objects.all())