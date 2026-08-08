from django.urls import path

from .views import print_pack_view

urlpatterns = [
    path("print-pack/", print_pack_view, name="print-pack"),
]
