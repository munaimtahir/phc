import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from apps.registry.models import Domain, Standard, Indicator, LabProfile


class Command(BaseCommand):
    help = "Load the locked Stage 0 registry and seed the Lab Profile."

    def handle(self, *args, **options):
        source = Path(__file__).resolve().parents[5] / "docs" / "data" / "indicators_master.json"
        try:
            records = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError(f"Unable to read canonical registry {source}: {exc}")
        if len(records) != 118:
            raise CommandError(f"Expected 118 indicators, found {len(records)}")

        for record in records:
            domain, _ = Domain.objects.update_or_create(code=record["domain_code"], defaults={"name": record["domain_name"]})
            standard, _ = Standard.objects.update_or_create(
                code=record["standard_code"],
                defaults={"domain": domain, "standard_no": record["standard_no"], "title": record["standard_title"]},
            )
            Indicator.objects.update_or_create(
                source_id=record["id"],
                defaults={"standard": standard, "text": record["indicator_text"], "weightage": record["weightage"],
                          "allows_partial": record["allows_partial"], "category": record["category"],
                          "frequency": record["frequency"], "evidence_format": record["evidence_format"],
                          "compliance_requirements": record["compliance_requirements"],
                          "survey_process": record["survey_process"],
                          "retention_months": 12 if record["category"] == "recurring" else None},
            )
        LabProfile.objects.update_or_create(id=1, defaults={
            "lab_name": "Al Shifa Laboratory", "address": "Circular Road, Jaranwala",
            "phc_registration_no": "P-20787", "supervising_pathologist": "Dr. Mubashr Ahmed",
        })
        self.stdout.write(self.style.SUCCESS(f"Loaded {Indicator.objects.count()} indicators across {Domain.objects.count()} domains."))
