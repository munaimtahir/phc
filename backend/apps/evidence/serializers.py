from rest_framework import serializers
from .models import EvidenceRecord
from .services import create_evidence


class EvidenceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceRecord
        fields = ["id", "indicator", "period_label", "submitted_at", "submitted_by", "status", "payload", "attachment", "is_current"]
        read_only_fields = ["id", "submitted_at", "is_current"]

    def validate(self, attrs):
        indicator = attrs["indicator"]
        if attrs["status"] == "partially_met" and not indicator.allows_partial:
            raise serializers.ValidationError("partially_met is not allowed for this indicator")
        if indicator.category == "recurring" and indicator.frequency != "as_needed" and not attrs.get("period_label"):
            raise serializers.ValidationError("period_label is required for recurring non_as_needed evidence")
        return attrs

    def create(self, validated_data):
        return create_evidence(**validated_data)
