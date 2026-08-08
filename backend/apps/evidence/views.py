import datetime

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status as http_status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.registry.models import Indicator
from .models import EvidenceRecord
from .serializers import EvidenceRecordSerializer
from .services import due_list, submit_evidence
from .structured_forms import schema_for


@api_view(["GET"])
def due_list_view(request):
    on_date_str = request.query_params.get("date")
    on_date = (
        datetime.date.fromisoformat(on_date_str) if on_date_str else datetime.date.today()
    )
    rows = due_list(on_date)
    data = [
        {
            "indicator_id": row["indicator"].id,
            "indicator_text": row["indicator"].text,
            "frequency": row["indicator"].frequency,
            "evidence_format": row["indicator"].evidence_format,
            "period_label": row["period_label"],
            "done": row["done"],
        }
        for row in rows
    ]
    return Response({"date": on_date.isoformat(), "items": data})


@api_view(["GET"])
def structured_form_schema_view(request, indicator_id):
    return Response({"indicator_id": indicator_id, "fields": schema_for(indicator_id)})


@api_view(["GET"])
def evidence_history_view(request, indicator_id):
    indicator = get_object_or_404(Indicator, pk=indicator_id)
    records = EvidenceRecord.objects.filter(indicator=indicator)
    return Response(EvidenceRecordSerializer(records, many=True).data)


@api_view(["POST"])
def submit_evidence_view(request):
    indicator_id = request.data.get("indicator")
    indicator = get_object_or_404(Indicator, pk=indicator_id)
    status_value = request.data.get("status")
    submitted_by = request.data.get("submitted_by") or getattr(request.user, "username", "") or "staff"
    file_obj = request.FILES.get("file")

    structured_data = {}
    if indicator.evidence_format == "structured_form":
        schema = schema_for(indicator.id)
        for field in schema:
            if field["name"] in request.data:
                structured_data[field["name"]] = request.data[field["name"]]
            elif field.get("required"):
                return Response(
                    {"detail": f"Missing required field: {field['name']}"},
                    status=http_status.HTTP_400_BAD_REQUEST,
                )

    try:
        record = submit_evidence(
            indicator=indicator,
            status=status_value,
            submitted_by=submitted_by,
            file=file_obj,
            structured_data=structured_data,
        )
    except ValidationError as exc:
        return Response({"detail": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)

    return Response(EvidenceRecordSerializer(record).data, status=http_status.HTTP_201_CREATED)
