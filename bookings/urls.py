from django.contrib import admin
from django.urls import path, include


from . import views
app_name = 'bookings'
urlpatterns = [
    path('', views.booking_view, name='bookings'),
    path('day/', views.day_view, name='day_view'),
    path('week/', views.week_view, name='week_view'),
    path('month/', views.month_view, name='month_view'),
    path('user-bookings/', views.get_user_bookings, name='user_bookings'),
    path('create/', views.CreateBookingView.as_view(), name='create_booking'),
    path('update/<int:pk>/', views.UpdateBookingView.as_view(), name='update_booking'),

    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]