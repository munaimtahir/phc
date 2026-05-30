from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_home, name='reports_home'),
    path('score-summary/', views.score_summary, name='report_score_summary'),
    path('missing-evidence/', views.missing_evidence, name='report_missing_evidence'),
    path('evidence-index/', views.evidence_index, name='report_evidence_index'),
    path('recurring/', views.recurring_compliance, name='report_recurring'),
    path('surveyor-pack/', views.surveyor_pack, name='report_surveyor_pack'),
]
