from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import DraftViewSet, indicator_template_view

router = DefaultRouter()
router.register("drafts", DraftViewSet, basename="draft")

urlpatterns = [
    path("template/<int:indicator_id>/", indicator_template_view, name="indicator-template"),
    path("", include(router.urls)),
]
