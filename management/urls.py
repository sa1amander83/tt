from django.urls import path

from .views import *

app_name = 'management'
urlpatterns = [
    path('', ManagementView.as_view(), {'active_tab': 'bookings'}, name='management-default'),  # URL /management/

    path('<str:active_tab>/', ManagementView.as_view(), name='management'),
    # path('bookings/', BookingListView.as_view(), name='bookings'),
    path('bookings/<int:pk>/', SingleBookingView.as_view(), name='booking_detail'),
    path('bookings/<int:pk>/update/', BookingUpdateView.as_view(), name='booking_update'),
    path('bookings/<int:pk>/delete/', BookingDeleteView.as_view(), name='booking_delete'),
    path('bookings/<int:pk>/cancel/', BookingCancelView.as_view(), name='cancel_booking'),

    # path('users/', UserListView.as_view(), name='users'),
    path('users/create/', UserCreateView.as_view(), name='create_user_profile'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_profile_delete'),
    path('users/<int:pk>/deactivate/', UserDeactivateView.as_view(), name='user_profile_deactivate'),
    path('users/<int:pk>/activate/', UserActivateView.as_view(), name='user_profile_activate'),
    path('users/<int:pk>/', AdminUserProfileView.as_view(), name='user_profile'),
    path('users/<int:pk>/update/', AdminUserProfileUpdateView.as_view(), name='user_profile_update'),
    path('users/<int:pk>/bookings/', AdminUserBookingsView.as_view(), name='user_bookings'),

]
