from django.urls import path


from .views import (
    ClubSettingsView, TableCreateView, TableUpdateView, TableDeleteView,
    TableTypeCreateView, PricingPlanCreateView, TableTypePricingCreateView,
    SpecialOfferCreateView, MembershipTypeCreateView, HolidayCreateView,
    ClubSettingsUpdateView, UpdateWorkingHoursView
)
app_name = 'admin_settings'
urlpatterns = [
    path('<str:active_tab>/', ClubSettingsView.as_view(), name='club_settings'),

    # Таблицы
    path('tables/create/', TableCreateView.as_view(), name='table_create'),
    path('tables/<int:pk>/update/', TableUpdateView.as_view(), name='table_update'),
    path('tables/<int:pk>/delete/', TableDeleteView.as_view(), name='table_delete'),
    path('table-types/create/', TableTypeCreateView.as_view(), name='table_type_create'),

    # Цены
    path('pricing-plans/create/', PricingPlanCreateView.as_view(), name='pricing_plan_create'),
    path('table-type-pricings/create/', TableTypePricingCreateView.as_view(),
         name='table_type_pricing_create'),
    path('special-offers/create/', SpecialOfferCreateView.as_view(), name='special_offer_create'),

    # Абонементы
    path('membership-types/create/', MembershipTypeCreateView.as_view(), name='membership_type_create'),

    # Расписание
    path('holidays/create/', HolidayCreateView.as_view(), name='holiday_create'),

    # Общие настройки
    path('general/update/', ClubSettingsUpdateView.as_view(), name='club_settings_update'),
    path('shedule/updateworkinghours/', UpdateWorkingHoursView.as_view(), name='update_working_hours'),
    path('general/update/', ClubSettingsUpdateView.as_view(), name='club_settings_update'),
    path('general/update/', ClubSettingsUpdateView.as_view(), name='club_settings_update'),
]