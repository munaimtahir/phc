from rest_framework import generics, status
from rest_framework.response import Response
from apps.registry.models import Indicator, LabProfile
from .models import Draft
from .serializers import DraftSerializer
from .services import eligible_kind, approve_draft, generate_content, generate_bulk_drafts


def draft_content(indicator, lab):
    return (f"{indicator.text}\n\nInstitution: {lab.lab_name}\nAddress: {lab.address}\n"
            f"PHC Registration: {lab.phc_registration_no}\nSupervising Pathologist: {lab.supervising_pathologist}\n\n"
            "Compliance requirements:\n- " + "\n- ".join(indicator.compliance_requirements) +
            "\n\nSurvey process:\n- " + "\n- ".join(indicator.survey_process))


class DraftListCreateView(generics.ListCreateAPIView):
    queryset = Draft.objects.select_related("indicator")
    serializer_class = DraftSerializer

    def perform_create(self, serializer):
        indicator = serializer.validated_data["indicator"]
        kind = eligible_kind(indicator)
        if not kind:
            raise ValueError("Drafts are only available for one-time or recurring documentary indicators")
        serializer.save(kind=kind, content=generate_content(indicator), status="draft")


class BulkDraftView(generics.GenericAPIView):
    def post(self, request):
        return Response(DraftSerializer(generate_bulk_drafts(), many=True).data, status=status.HTTP_201_CREATED)


class ApprovedTemplateView(generics.GenericAPIView):
    def get(self, request, indicator_id):
        draft = Draft.objects.filter(indicator_id=indicator_id, kind="template", status="approved").order_by("-version_no", "-id").first()
        if not draft:
            return Response({"detail": "No approved template exists"}, status=status.HTTP_404_NOT_FOUND)
        return Response(DraftSerializer(draft).data)


class DraftApproveView(generics.GenericAPIView):
    queryset = Draft.objects.select_related("indicator")

    def post(self, request, pk):
        draft = self.get_object()
        try:
            approve_draft(draft, request.data.get("reviewed_by"))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(DraftSerializer(draft).data)
