from django.urls import path
from .views import DomainListView, StandardListView, IndicatorListView, LabProfileView

urlpatterns = [
    path("domains/", DomainListView.as_view()),
    path("standards/", StandardListView.as_view()),
    path("indicators/", IndicatorListView.as_view()),
    path("lab-profile/", LabProfileView.as_view()),
]
