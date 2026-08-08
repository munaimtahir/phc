from rest_framework import serializers
from .models import Draft


class DraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Draft
        fields = ["id", "indicator", "kind", "content", "generated_at", "status", "reviewed_by", "reviewed_at", "version_no"]
        read_only_fields = ["id", "generated_at", "status", "reviewed_by", "reviewed_at", "version_no"]
