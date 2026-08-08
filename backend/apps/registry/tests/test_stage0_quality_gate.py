import json
import random

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from apps.registry.models import Domain, Standard, Indicator, LabProfile

EXPECTED_DOMAIN_COUNTS = {
    "AAC": 9, "BSBS": 18, "COP": 6, "FMS": 11, "HRM": 16,
    "MER": 13, "PRE": 7, "QA": 16, "ROM": 13, "RRS": 9,
}


class Stage0QualityGateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("load_indicators")

    def test_exactly_118_indicators_no_gaps_no_duplicates(self):
        ids = sorted(Indicator.objects.values_list("id", flat=True))
        self.assertEqual(ids, list(range(1, 119)))

    def test_per_domain_counts(self):
        for code, expected in EXPECTED_DOMAIN_COUNTS.items():
            domain = Domain.objects.get(code=code)
            count = Indicator.objects.filter(standard__domain=domain).count()
            self.assertEqual(count, expected, f"domain {code}")

    def test_37_distinct_standards(self):
        self.assertEqual(Standard.objects.count(), 37)

    def test_weightage_split(self):
        self.assertEqual(Indicator.objects.filter(weightage=100).count(), 97)
        self.assertEqual(Indicator.objects.filter(weightage=80).count(), 21)
        self.assertEqual(Indicator.objects.filter(allows_partial=True).count(), 21)

    def test_category_split(self):
        self.assertEqual(Indicator.objects.filter(category="physical").count(), 29)
        self.assertEqual(Indicator.objects.filter(category="one_time").count(), 32)
        self.assertEqual(Indicator.objects.filter(category="recurring").count(), 57)

    def test_recurring_has_frequency_others_null(self):
        self.assertFalse(
            Indicator.objects.filter(category="recurring", frequency__isnull=True).exists()
        )
        self.assertFalse(
            Indicator.objects.exclude(category="recurring").exclude(frequency__isnull=True).exists()
        )

    def test_evidence_format_split(self):
        self.assertEqual(Indicator.objects.filter(evidence_format="photo").count(), 69)
        self.assertEqual(Indicator.objects.filter(evidence_format="document").count(), 44)
        self.assertEqual(Indicator.objects.filter(evidence_format="structured_form").count(), 5)

    def test_spot_check_matches_source_json_byte_for_byte(self):
        with open(settings.INDICATORS_MASTER_PATH) as f:
            records = {r["id"]: r for r in json.load(f)}
        sample_ids = random.sample(list(records.keys()), 10)
        for indicator_id in sample_ids:
            source = records[indicator_id]
            db = Indicator.objects.get(id=indicator_id)
            self.assertEqual(db.text, source["indicator_text"])
            self.assertEqual(db.compliance_requirements, source["compliance_requirements"])
            self.assertEqual(db.weightage, source["weightage"])

    def test_lab_profile_seeded_exactly(self):
        profile = LabProfile.load()
        self.assertEqual(profile.lab_name, "Al Shifa Laboratory")
        self.assertEqual(profile.address, "Circular Road, Jaranwala")
        self.assertEqual(profile.phc_registration_no, "P-20787")
        self.assertEqual(profile.supervising_pathologist, "Dr. Mubashr Ahmed")

    def test_registry_filter_domain_rom_returns_13(self):
        client = APIClient()
        resp = client.get("/api/registry/indicators/?domain=ROM")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()["results"] if "results" in resp.json() else resp.json()), 13)

    def test_registry_filter_category_recurring_returns_57(self):
        client = APIClient()
        resp = client.get("/api/registry/indicators/?category=recurring")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        results = data["results"] if isinstance(data, dict) and "results" in data else data
        self.assertEqual(len(results), 57)
