from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('bun/', include('bun.urls')),
    path('ctg/', include('ctg.urls')),
    path('bar/', include('bar.urls')),
    path('api/', include('api.urls')),
    path('api_data/', include('consumirapi.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)


