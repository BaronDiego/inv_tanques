from django.urls import path
from . import views

urlpatterns = [
    path('data_api/', views.api_json, name='api_prueba')
]
