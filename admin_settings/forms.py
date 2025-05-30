from django import forms

from admin_settings.models import Holiday, ClubSettings, WorkingDay, Table, TableType
from bookings.models import TableTypePricing


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
from admin_settings.models import Holiday, ClubSettings


class TableTypeForm(forms.ModelForm):
    class Meta:
        model = TableType
        fields = ['name', 'description', 'max_capacity']
        labels = {
            'name': 'Название типа',
            'description': 'Описание',
            'max_capacity': 'Вместимость',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md border-2 border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'max_capacity': forms.NumberInput(attrs={
                'class': 'w-full sm:w-1/2 mt-1 block rounded-md  border-2 border-2 border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
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
