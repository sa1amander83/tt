from django.contrib import admin
from django.urls import path, include

from main.views import *

app_name = 'main'
urlpatterns = [

path('', IndexView.as_view(), name='index'),
path('terms/', terms, name='terms'),
path('contacts/', contacts_view, name='contacts'),
path('about/', about_view, name='about'),


]