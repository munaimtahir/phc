from django.urls import path
from . import views

app_name = 'indicators'
urlpatterns = [
    path('', views.indicator_list, name='list'),
    path('<int:pk>/', views.indicator_detail, name='detail'),
]
