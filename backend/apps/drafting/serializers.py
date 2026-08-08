from rest_framework import serializers
from .models import Draft


class DraftSerializer(serializers.ModelSerializer):
    indicator = serializers.ReadOnlyField(source="indicator_id")

    class Meta:
        model = Draft
        fields = [
            "id",
            "indicator",
            "indicator_ids",
            "kind",
            "template_version",
            "prompt_text",
            "raw_output",
            "working_content",
            "content",
            "status",
            "created_by",
            "created_at",
            "reviewed_by",
            "reviewed_at",
            "version_no",
            "linked_document_id",
        ]
        read_only_fields = [
            "id",
            "kind",
            "prompt_text",
            "created_at",
            "reviewed_by",
            "reviewed_at",
            "version_no",
        ]
