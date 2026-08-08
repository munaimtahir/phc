from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import authenticate
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["POST"])
def login_view(request):
    """Validates the shared-login credentials. The frontend keeps the
    credentials client-side and sends them as HTTP Basic auth on every
    subsequent request — there is no server-side session to start here.
    """
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response({"detail": "Invalid credentials."}, status=401)
    return Response({"username": user.username})


@api_view(["GET"])
def whoami_view(request):
    if request.user.is_authenticated:
        return Response({"username": request.user.username})
    return Response({"username": None})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login/", login_view, name="login"),
    path("api/auth/whoami/", whoami_view, name="whoami"),
    path("api/registry/", include("apps.registry.urls")),
    path("api/evidence/", include("apps.evidence.urls")),
    path("api/compliance/", include("apps.compliance.urls")),
    path("api/exports/", include("apps.exports.urls")),
    path("api/drafting/", include("apps.drafting.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
