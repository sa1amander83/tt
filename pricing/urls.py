from django.urls import path

from .views import *

app_name = 'pricing'
urlpatterns = [
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
]