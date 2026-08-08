from rest_framework import generics
from .models import Domain, Standard, Indicator, LabProfile
from .serializers import DomainSerializer, StandardSerializer, IndicatorSerializer, LabProfileSerializer


class DomainListView(generics.ListAPIView):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer


class StandardListView(generics.ListAPIView):
    serializer_class = StandardSerializer

    def get_queryset(self):
        queryset = Standard.objects.select_related("domain")
        domain = self.request.query_params.get("domain")
        return queryset.filter(domain__code=domain) if domain else queryset


class IndicatorListView(generics.ListAPIView):
    serializer_class = IndicatorSerializer

    def get_queryset(self):
        queryset = Indicator.objects.select_related("standard__domain")
        for param, field in (("domain", "standard__domain__code"), ("standard", "standard__code"),
                             ("category", "category"), ("frequency", "frequency")):
            value = self.request.query_params.get(param)
            if value:
                queryset = queryset.filter(**{field: value})
        return queryset


class LabProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = LabProfileSerializer

    def get_object(self):
        return LabProfile.objects.order_by("id").first()
