from rest_framework import serializers

from .models import EvidenceRecord


class EvidenceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceRecord
        fields = [
            "id",
            "indicator",
            "period_label",
            "submitted_at",
            "submitted_by",
            "status",
            "file",
            "structured_data",
            "is_current",
        ]
        read_only_fields = ["id", "submitted_at", "is_current"]
