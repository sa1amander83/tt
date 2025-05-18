from django.urls import path

from .views import *

app_name = 'admin_settings'
urlpatterns = [
    path('<str:active_tab>/', ClubSettingsView.as_view(), name='club_settings'),

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
    path('pricing-plans/create/', PricingPlanCreateView.as_view(), name='pricing_plan_create'),
    path('pricing-plans/<int:pk>/', PricingPlanView.as_view(), name='pricing_plan_view'),

    path('pricing-plans/<int:pk>/update/', PricingPlanUpdateView.as_view(), name='pricing_plan_update'),
    path('pricing-plans/<int:pk>/delete/', PricingPlanDeleteView.as_view(), name='pricing_plan_delete'),

    path('table-type-pricings/create/', TableTypePricingCreateView.as_view(), name='table_type_pricing_create'),
    path('table-type-pricings/<int:pk>/', TableTypePricingView.as_view(), name='table_type_pricing_view'),

    path('table-type-pricings/<int:pk>/update/', TableTypePricingUpdateView.as_view(),
         name='table_type_pricing_update'),
    path('table-type-pricings/<int:pk>/delete/', TableTypePricingDeleteView.as_view(),
         name='table_type_pricing_delete'),
    path('special-offers/create/', SpecialOfferCreateView.as_view(), name='special_offer_create'),
    path('special-offers/<int:pk>/', SpecialOfferView.as_view(), name='special_offer_view'),
    path('special-offers/<int:pk>/update/', SpecialOfferUpdateView.as_view(), name='special_offer_update'),
    path('special-offers/<int:pk>/delete/', SpecialOfferDeleteView.as_view(), name='special_offer_delete'),
    # Абонементы
    path('membership/create/', MembershipCreateView.as_view(), name='membership_type_create'),
    path('membership/<int:pk>/update/', MembershipUpdateView.as_view(), name='membership_type_update'),
    path('membership/<int:pk>/view/', MembershipView.as_view(), name='membership_type_view'),
    path('membership/<int:pk>/delete/', MembershipDeleteView.as_view(), name='membership_type_delete'),

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





]
