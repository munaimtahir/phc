from django.urls import include, path

urlpatterns = [path("api/", include("apps.registry.urls"))]
urlpatterns += [path("api/evidence/", include("apps.evidence.urls")), path("api/drafting/", include("apps.drafting.urls")), path("api/exports/", include("apps.exports.urls"))]
