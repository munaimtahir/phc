from django.urls import path

from .views import compliance_view

urlpatterns = [
    path("", compliance_view, name="compliance"),
]
