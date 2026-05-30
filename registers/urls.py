from django.urls import path
from . import views

urlpatterns = [
    path('', views.register_list, name='register_list'),
    path('<int:pk>/', views.register_detail, name='register_detail'),
    path('<int:pk>/entries/add/', views.add_entry, name='register_entry_add'),
    path('<int:pk>/print/', views.register_print, name='register_print'),
]
