from datetime import date
from rest_framework import generics
from rest_framework.response import Response
from .models import EvidenceRecord
from .serializers import EvidenceRecordSerializer
from .services import due_list, compliance_summary


class EvidenceListCreateView(generics.ListCreateAPIView):
    queryset = EvidenceRecord.objects.select_related("indicator")
    serializer_class = EvidenceRecordSerializer


class DueListView(generics.GenericAPIView):
    def get(self, request):
        requested = request.query_params.get("date")
        on_date = date.fromisoformat(requested) if requested else date.today()
        return Response([{"indicator_id": item["indicator"].source_id, "period_label": item["period_label"],
                          "has_evidence": item["has_evidence"]} for item in due_list(on_date)])


class ComplianceView(generics.GenericAPIView):
    def get(self, request):
        return Response(compliance_summary())
