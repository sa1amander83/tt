from django.contrib import admin
from django.urls import path, include

from .views import BookingsView

app_name = 'bookings'
urlpatterns = [
path('', BookingsView.as_view(), name='bookings'),
]