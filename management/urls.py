from django.urls import path

from .management_views import *
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
    path('bookings/ajax/', ManagementBookingsAjaxView.as_view(), name='bookings_ajax'),

    # path('users/', UserListView.as_view(), name='users'),
    path('users/create/', UserCreateView.as_view(), name='create_user_profile'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_profile_delete'),
    path('users/<int:pk>/deactivate/', UserDeactivateView.as_view(), name='user_profile_deactivate'),
    path('users/<int:pk>/activate/', UserActivateView.as_view(), name='user_profile_activate'),
    path('users/<int:pk>/', AdminUserProfileView.as_view(), name='user_profile'),
    path('users/<int:pk>/update/', AdminUserProfileUpdateView.as_view(), name='user_profile_update'),
    path('users/<int:pk>/bookings/', AdminUserBookingsView.as_view(), name='user_bookings'),

    path('special-offers/create/', SpecialOfferCreateView.as_view(), name='special_offer_create'),
    path('special-offers/<int:pk>/', SpecialOfferView.as_view(), name='special_offer_view'),
    path('special-offers/<int:pk>/update/', SpecialOfferUpdateView.as_view(), name='special_offer_update'),
    path('special-offers/<int:pk>/delete/', SpecialOfferDeleteView.as_view(), name='special_offer_delete'),


    path('membership/create/', MembershipCreateView.as_view(), name='membership_type_create'),
    path('membership/<int:pk>/update/', MembershipUpdateView.as_view(), name='membership_type_update'),
    path('membership/<int:pk>/view/', MembershipView.as_view(), name='membership_type_view'),
    path('membership/<int:pk>/delete/', MembershipDeleteView.as_view(), name='membership_type_delete'),
path('promocodes/create/', create_promocode, name='create_promocode'),

   # path('promocodes/', PromoCodeListCreate.as_view(), name='promocode-list'),
    path('promocodes/<int:pk>/', PromoCodeDetail.as_view(), name='promocode-detail'),
    path('promocodes/', PromoCodeManagementView.as_view(), name='promocode-management'),
    path('validate-promo/', ValidatePromoCode.as_view(), name='validate-promo'),

    path('loyalty/add-benefit/', add_level_benefit, name='add_level_benefit'),

]


from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PromoCodeViewSet

router = DefaultRouter()
router.register(r'promocodes', PromoCodeViewSet, basename='promocode')

urlpatterns = [
    path('api/', include(router.urls)),
]
