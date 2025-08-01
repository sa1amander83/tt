from django.urls import path


from .views import *

app_name = 'admin_settings'
urlpatterns = [

    # Таблицы
    path('tables/create/', TableCreateView.as_view(), name='table_create'),
    path('tables/<int:pk>/', TableDetailView.as_view(), name='table_detail'),
    path('tables/<int:pk>/update/', TableUpdateView.as_view(), name='table_update'),
    path('tables/<int:pk>/delete/', TableDeleteView.as_view(), name='table_delete'),
    path('table-types/create/', TableTypeCreateView.as_view(), name='table_type_create'),
    path('table-types/<int:pk>/', TableTypeView.as_view(), name='table_type_view'),
    path('table-types/<int:pk>/update/', TableTypeUpdateView.as_view(), name='table_type_update'),
    path('table-types/<int:pk>/delete/', TableTypeDeleteView.as_view(), name='table_type_delete'),





    # Цены
    path('set-max-unpaid-bookings/', set_max_unpaid_bookings, name='set_max_unpaid_bookings'),
    path('get-max-unpaid-bookings/', get_max_unpaid_bookings, name='get_max_unpaid_bookings'),
    # Расписание
    path('holidays/create/', HolidayCreateView.as_view(), name='holiday_create'),

    # Общие настройки
    path('general/update/', ClubSettingsUpdateView.as_view(), name='club_settings_update'),
    path('schedule/update-working-hours/', UpdateWorkingHoursView.as_view(), name='update_working_hours'),
    path('general/update/', ClubSettingsUpdateView.as_view(), name='club_settings_update'),
    # path('schedule/', ScheduleSettingsView.as_view(), name='schedule'),

    path('holidays/create/', HolidayCreateView.as_view(), name='holiday_create'),
    path('holidays/<int:pk>/', HolidayView.as_view(), name='holiday_view'),
    path('holidays/<int:pk>/update/', HolidayUpdateView.as_view(), name='holiday_update'),
    path('holidays/<int:pk>/delete/', HolidayDeleteView.as_view(), name='holiday_delete'),

    path('api/equipment/create/', create_equipment, name='create_equipment'),
    path('api/equipment/<int:equip_id>/update/', update_equipment, name='update_equipment'),
    path('api/equipment/<int:equip_id>/delete/', delete_equipment, name='delete_equipment'),
    path('api/equipment/<int:equip_id>/', get_equipment, name='get_equipment'),

    path('set-max-unpaid-bookings/', set_max_unpaid_bookings, name='set_max_unpaid_bookings'),
    path('get-max-unpaid-bookings/', get_max_unpaid_bookings, name='get_max_unpaid_bookings'),
    path('<str:active_tab>/', ClubSettingsView.as_view(), name='club_settings'),

]
