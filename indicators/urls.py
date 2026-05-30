from django.urls import path
from . import views

urlpatterns = [
    path('', views.indicator_list, name='indicator_list'),
    path('<int:pk>/', views.indicator_detail, name='indicator_detail'),
    path('<int:pk>/prompt/<int:req_pk>/', views.generate_prompt_view, name='generate_prompt'),
]
