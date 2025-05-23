from django.urls import path


from .views import *
app_name='events'

urlpatterns = [
    path('', BookingListView.as_view(), name='booking-list'),
    path('calendar/', CalendarView.as_view(), name='calendar'),

    path('<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),

    path('<int:pk>/pay/', PaymentHandlerView.as_view(), name='initiate-payment'),
    path('<int:pk>/payment-callback/', PaymentCallbackView.as_view(), name='payment-callback'),
]