from django.urls import path
from . import views

urlpatterns = [
    path('data_api/', views.api_json, name='api_prueba'),
    path('data_post/', views.api_post, name='api_post')
]
