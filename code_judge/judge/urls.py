from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
   path('',views.custom_test, name='custom_test'),
]
