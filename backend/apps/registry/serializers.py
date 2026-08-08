from rest_framework import serializers
from .models import Domain, Standard, Indicator, LabProfile


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ["id", "code", "name"]


class StandardSerializer(serializers.ModelSerializer):
    domain_code = serializers.CharField(source="domain.code", read_only=True)

    class Meta:
        model = Standard
        fields = ["id", "domain", "domain_code", "standard_no", "code", "title"]


class IndicatorSerializer(serializers.ModelSerializer):
    standard_code = serializers.CharField(source="standard.code", read_only=True)
    domain_code = serializers.CharField(source="standard.domain.code", read_only=True)
    domain_name = serializers.CharField(source="standard.domain.name", read_only=True)

    class Meta:
        model = Indicator
        fields = ["id", "source_id", "standard", "standard_code", "domain_code", "domain_name", "text",
                  "weightage", "allows_partial", "category", "frequency", "evidence_format",
                  "compliance_requirements", "survey_process", "retention_months"]


class LabProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabProfile
        fields = ["id", "lab_name", "address", "phc_registration_no", "supervising_pathologist", "updated_at"]
        read_only_fields = ["id", "updated_at"]
