from django.urls import path
from . import views

app_name = 'registers'
urlpatterns = [
    path('', views.register_list, name='list'),
    path('<int:pk>/', views.register_detail, name='detail'),
    path('<int:pk>/add/', views.register_add_entry, name='add_entry'),
]
