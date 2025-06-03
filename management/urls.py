from django.urls import path

from .views import *

app_name = 'management'
urlpatterns = [
path('', ManagementView.as_view(), name='management'),
    path('bookings/', BookingListView.as_view(), name='bookings'),
    # path('bookings/<int:pk>/update/', BookingUpdateView.as_view(), name='booking_update'),
    # path('bookings/<int:pk>/delete/', BookingDeleteView.as_view(), name='booking_delete'),
    # path('bookings/<int:pk>/cancel/', cancel_booking, name='cancel-booking'),
    #
    path('users/', UserListView.as_view(), name='users'),
    # path('users/<int:pk>/update/', UserUpdateView.as_view(), name='user_update'),
    # path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),

    path('reports/', ReportsView.as_view(), name='reports'),

]
