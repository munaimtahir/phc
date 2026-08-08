import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.registry.models import Domain, Standard, Indicator, LabProfile

RECURRING_DEFAULT_RETENTION_MONTHS = 12

LAB_PROFILE_SEED = {
    "lab_name": "Al Shifa Laboratory",
    "address": "Circular Road, Jaranwala",
    "phc_registration_no": "P-20787",
    "supervising_pathologist": "Dr. Mubashr Ahmed",
}


class Command(BaseCommand):
    help = "Load the canonical indicators_master.json into the registry, and seed LabProfile."

    @transaction.atomic
    def handle(self, *args, **options):
        with open(settings.INDICATORS_MASTER_PATH) as f:
            records = json.load(f)

        domains = {}
        standards = {}

        for rec in records:
            domain, _ = Domain.objects.update_or_create(
                code=rec["domain_code"],
                defaults={"name": rec["domain_name"]},
            )
            domains[rec["domain_code"]] = domain

            standard, _ = Standard.objects.update_or_create(
                code=rec["standard_code"],
                defaults={
                    "domain": domain,
                    "standard_no": rec["standard_no"],
                    "title": rec["standard_title"],
                },
            )
            standards[rec["standard_code"]] = standard

            retention_months = (
                RECURRING_DEFAULT_RETENTION_MONTHS if rec["category"] == "recurring" else None
            )

            Indicator.objects.update_or_create(
                id=rec["id"],
                defaults={
                    "standard": standard,
                    "text": rec["indicator_text"],
                    "weightage": rec["weightage"],
                    "allows_partial": rec["allows_partial"],
                    "category": rec["category"],
                    "frequency": rec["frequency"],
                    "evidence_format": rec["evidence_format"],
                    "compliance_requirements": rec["compliance_requirements"],
                    "survey_process": rec["survey_process"],
                    "scoring": rec["scoring"],
                    "guidelines": rec["guidelines"],
                    "retention_months": retention_months,
                    "classification_source": rec["classification_source"],
                    "classification_note": rec["classification_note"],
                },
            )

        LabProfile.objects.update_or_create(pk=1, defaults=LAB_PROFILE_SEED)

        self.stdout.write(self.style.SUCCESS(
            f"Loaded {Indicator.objects.count()} indicators, "
            f"{Standard.objects.count()} standards, {Domain.objects.count()} domains."
        ))
