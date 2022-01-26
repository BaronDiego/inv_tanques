from django.urls import path, include
from .views import home, HomeSinPrevilegios, panel

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('', home, name='home'),
    path('panel/', panel ,name='panel'),
    path('sin_privilegios/', HomeSinPrevilegios.as_view(), name='sin_privilegios')
]