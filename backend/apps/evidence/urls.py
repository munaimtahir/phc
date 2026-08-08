from django.urls import path
from .views import EvidenceListCreateView, DueListView, ComplianceView

urlpatterns = [path("records/", EvidenceListCreateView.as_view()), path("due-list/", DueListView.as_view()), path("compliance/", ComplianceView.as_view())]
