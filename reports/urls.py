from django.urls import path
from . import views

app_name = 'reports'
urlpatterns = [
    path('', views.report_index, name='index'),
    path('score-summary/', views.score_summary, name='score_summary'),
    path('missing-evidence/', views.missing_evidence, name='missing_evidence'),
    path('surveyor-pack/', views.surveyor_pack, name='surveyor_pack'),
]
