import django_filters
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Domain, Standard, Indicator, LabProfile
from .serializers import (
    DomainSerializer,
    StandardSerializer,
    IndicatorSerializer,
    LabProfileSerializer,
)


class DomainViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer


class StandardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Standard.objects.select_related("domain").all()
    serializer_class = StandardSerializer
    filterset_fields = ["domain__code"]


class IndicatorFilter(django_filters.FilterSet):
    domain = django_filters.CharFilter(field_name="standard__domain__code")
    standard = django_filters.CharFilter(field_name="standard__code")
    category = django_filters.CharFilter(field_name="category")
    frequency = django_filters.CharFilter(field_name="frequency")

    class Meta:
        model = Indicator
        fields = ["domain", "standard", "category", "frequency", "evidence_format"]


class IndicatorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Indicator.objects.select_related("standard", "standard__domain").all()
    serializer_class = IndicatorSerializer
    filterset_class = IndicatorFilter


@api_view(["GET"])
def lab_profile_view(request):
    profile = LabProfile.load()
    return Response(LabProfileSerializer(profile).data)
