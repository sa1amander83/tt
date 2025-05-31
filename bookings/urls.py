from django.contrib import admin
from django.urls import path, include


from . import views
from .views import yookassa_webhook

app_name = 'bookings'
urlpatterns = [
    path('', views.booking_view, name='bookings'),
    # path('day/', views.day_view, name='day_view'),
    # path('week/', views.week_api_view, name='week_view'),
    # path('month/', views.month_view, name='month_view'),
    # path('user-bookings/', views.get_user_bookings, name='user_bookings'),
    path('create/', views.CreateBookingView.as_view(), name='create_booking'),
    path('update/<int:pk>/', views.UpdateBookingView.as_view(), name='update_booking'),

    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('api/get-booking-info/', views.get_booking_info, name='get_booking_info'),
    path('api/rates/', views.booking_rates_api, name='api_rates'),
    path('api/tables/', views.tables_api, name='api_tables'),
    path('api/calendar/', views.CalendarAPIView.as_view(), name='api_calendar'),
    # path('api/week/', views.week_calendar_api, name='week_calendar'),

    path('api/user-bookings/', views.get_user_bookings, name='api_user_bookings'),
    path('api/calculate/', views.calculate_booking_api, name='api_calculate'),
    path('api/create/', views.create_booking_api, name='api_create'),
    path('api/payment/', views.create_yookassa_payment, name='api_payment'),
    path('api/payment/callback/<int:booking_id>/', views.payment_callback, name='payment_callback'),

    path('api/site-settings/', views.get_site_settings, name='site-settings'),

    path('api/yookassa/webhook/', yookassa_webhook, name='yookassa_webhook'),


]