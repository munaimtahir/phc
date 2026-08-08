from django.urls import path
from .views import PrintPackView

urlpatterns = [path("print-pack/", PrintPackView.as_view())]
