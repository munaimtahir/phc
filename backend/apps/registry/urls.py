from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import DomainViewSet, StandardViewSet, IndicatorViewSet, lab_profile_view

router = DefaultRouter()
router.register("domains", DomainViewSet)
router.register("standards", StandardViewSet)
router.register("indicators", IndicatorViewSet)

urlpatterns = [
    path("lab-profile/", lab_profile_view, name="lab-profile"),
    path("", include(router.urls)),
]
