from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status as http_status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from apps.registry.models import Indicator
from .models import Draft
from .serializers import DraftSerializer
from .services import (
    create_prompt_draft,
    save_raw_output,
    update_working_content,
    approve_draft,
    reject_draft,
    eligible_indicators,
)


class DraftViewSet(viewsets.ModelViewSet):
    queryset = Draft.objects.all()
    serializer_class = DraftSerializer
    filterset_fields = ["status", "kind"]

    @action(detail=False, methods=["get"])
    def eligible_indicators_list(self, request):
        return Response([ind.id for ind in eligible_indicators()])

    @action(detail=False, methods=["post"])
    def build_prompt(self, request):
        indicator_ids = request.data.get("indicator_ids")
        if not indicator_ids and request.data.get("indicator"):
            indicator_ids = [request.data.get("indicator")]

        if not indicator_ids:
            return Response(
                {"detail": "indicator_ids parameter is required."},
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        created_by = request.data.get("created_by") or getattr(request.user, "username", "")
        existing_draft_id = request.data.get("existing_draft_id")

        try:
            draft = create_prompt_draft(
                indicator_ids=indicator_ids,
                created_by=created_by,
                existing_draft_id=existing_draft_id,
            )
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)

        return Response(DraftSerializer(draft).data, status=http_status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def generate(self, request):
        # Backwards compatible alias for build_prompt
        return self.build_prompt(request)

    @action(detail=True, methods=["post"])
    def save_output(self, request, pk=None):
        draft = self.get_object()
        raw_output = request.data.get("raw_output", "")
        try:
            draft = save_raw_output(draft, raw_output)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        return Response(DraftSerializer(draft).data)

    @action(detail=True, methods=["post", "patch"])
    def update_content(self, request, pk=None):
        draft = self.get_object()
        working_content = request.data.get("working_content", "")
        try:
            draft = update_working_content(draft, working_content)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        return Response(DraftSerializer(draft).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        draft = self.get_object()
        reviewed_by = request.data.get("reviewed_by") or getattr(request.user, "username", "")
        try:
            draft = approve_draft(draft, reviewed_by)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        return Response(DraftSerializer(draft).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        draft = self.get_object()
        reviewed_by = request.data.get("reviewed_by") or getattr(request.user, "username", "")
        try:
            draft = reject_draft(draft, reviewed_by)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        return Response(DraftSerializer(draft).data)


@api_view(["GET"])
def indicator_template_view(request, indicator_id):
    indicator_id = int(indicator_id)
    template = (
        Draft.objects.filter(indicator_ids__contains=[indicator_id], kind="template", status="approved")
        .order_by("-version_no")
        .first()
    )
    if template is None:
        return Response({"detail": "No approved template for this indicator."}, status=http_status.HTTP_404_NOT_FOUND)
    return Response(DraftSerializer(template).data)
