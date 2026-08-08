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
    domain_code = serializers.CharField(source="standard.domain.code", read_only=True)
    domain_name = serializers.CharField(source="standard.domain.name", read_only=True)
    standard_code = serializers.CharField(source="standard.code", read_only=True)
    standard_title = serializers.CharField(source="standard.title", read_only=True)

    class Meta:
        model = Indicator
        fields = [
            "id",
            "standard",
            "domain_code",
            "domain_name",
            "standard_code",
            "standard_title",
            "text",
            "weightage",
            "allows_partial",
            "category",
            "frequency",
            "evidence_format",
            "compliance_requirements",
            "survey_process",
            "scoring",
            "guidelines",
            "retention_months",
            "classification_source",
            "classification_note",
        ]


class LabProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabProfile
        fields = ["lab_name", "address", "phc_registration_no", "supervising_pathologist"]
