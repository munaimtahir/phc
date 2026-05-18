from django.contrib import admin
from django.urls import path, include
from core.views import dashboard, health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('indicators/', include('indicators.urls')),
    path('evidence/', include('evidence.urls')),
    path('registers/', include('registers.urls')),
    path('reports/', include('reports.urls')),
    path('', dashboard, name='dashboard'),
]
