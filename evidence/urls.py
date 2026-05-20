from django.urls import path
from . import views

app_name = 'evidence'
urlpatterns = [
    path('', views.evidence_list, name='list'),
    path('add/', views.evidence_create, name='add'),
    path('<int:pk>/', views.evidence_detail, name='detail'),
    path('<int:pk>/link/', views.evidence_link, name='link'),
]
