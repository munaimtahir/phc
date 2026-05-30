from django.contrib import admin
from django.urls import path, include
from core.views import health_check, dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', dashboard, name='dashboard'),
    
    # We will include other apps later
    path('indicators/', include('indicators.urls')),
    path('evidence/', include('evidence.urls')),
    path('registers/', include('registers.urls')),
    path('reports/', include('reports.urls')),
]
