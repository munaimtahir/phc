import json
from pathlib import Path
from datetime import date, timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from apps.registry.models import Indicator, LabProfile
from apps.evidence.models import EvidenceRecord
from apps.evidence.services import create_evidence, due_list, compliance_summary, prune_old_evidence, period_label
from apps.drafting.models import Draft
from apps.drafting.services import approve_draft, eligible_kind, generate_bulk_drafts


class FullQualityGateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command
        call_command("seed_registry", verbosity=0)

    def test_stage_0_registry_gate(self):
        source = json.loads((Path(__file__).resolve().parents[3] / "docs/data/indicators_master.json").read_text())
        self.assertEqual(list(Indicator.objects.values_list("source_id", flat=True).order_by("source_id")), list(range(1, 119)))
        self.assertEqual(Indicator.objects.count(), 118)
        self.assertEqual(Indicator.objects.values("standard").distinct().count(), 37)
        self.assertEqual({code: Indicator.objects.filter(standard__domain__code=code).count() for code in ["AAC", "BSBS", "COP", "FMS", "HRM", "MER", "PRE", "QA", "ROM", "RRS"]},
                         {"AAC": 9, "BSBS": 18, "COP": 6, "FMS": 11, "HRM": 16, "MER": 13, "PRE": 7, "QA": 16, "ROM": 13, "RRS": 9})
        self.assertEqual(Indicator.objects.filter(weightage=100).count(), 97)
        self.assertEqual(Indicator.objects.filter(weightage=80, allows_partial=True).count(), 21)
        self.assertEqual(Indicator.objects.filter(category="physical").count(), 29)
        self.assertEqual(Indicator.objects.filter(category="one_time").count(), 32)
        self.assertEqual(Indicator.objects.filter(category="recurring").count(), 57)
        self.assertFalse(Indicator.objects.filter(category="recurring", frequency__isnull=True).exists())
        self.assertFalse(Indicator.objects.filter(category__in=["physical", "one_time"], frequency__isnull=False).exists())
        self.assertEqual(Indicator.objects.filter(evidence_format="photo").count(), 69)
        self.assertEqual(Indicator.objects.filter(evidence_format="document").count(), 44)
        self.assertEqual(Indicator.objects.filter(evidence_format="structured_form").count(), 5)
        for record in source[::12]:
            db = Indicator.objects.get(source_id=record["id"])
            self.assertEqual(db.text, record["indicator_text"])
            self.assertEqual(db.compliance_requirements, record["compliance_requirements"])
            self.assertEqual(db.weightage, record["weightage"])
        profile = LabProfile.objects.get()
        self.assertEqual((profile.lab_name, profile.address, profile.phc_registration_no, profile.supervising_pathologist),
                         ("Al Shifa Laboratory", "Circular Road, Jaranwala", "P-20787", "Dr. Mubashr Ahmed"))
        client = APIClient()
        self.assertEqual(len(client.get("/api/indicators/?domain=ROM").json()), 13)
        self.assertEqual(len(client.get("/api/indicators/?category=recurring").json()), 57)

    def test_stage_1_gate(self):
        indicators = list(Indicator.objects.order_by("source_id")[:10])
        for i, status in zip(indicators, ["fully_met", "partially_met", "not_met"] * 4):
            if status == "partially_met" and not i.allows_partial:
                status = "fully_met"
            label = period_label(i, date(2026, 8, 7)) if i.category == "recurring" and i.frequency != "as_needed" else None
            create_evidence(indicator=i, submitted_by="tester", status=status, payload={}, period_label=label)
        summary = compliance_summary()
        self.assertEqual(summary["possible_weightage"], sum(i.weightage for i in Indicator.objects.all()))
        self.assertGreaterEqual(summary["compliance_percent"], 0)
        recurring = Indicator.objects.filter(category="recurring").exclude(frequency="as_needed").first()
        self.assertEqual(len(due_list(date(2026, 8, 7))), Indicator.objects.filter(category="recurring").exclude(frequency="as_needed").count())
        self.assertNotIn(recurring.source_id, [x["indicator"].source_id for x in due_list(date(2026, 8, 7)) if x["has_evidence"] and x["period_label"] != period_label(recurring, date(2026, 8, 7))])
        non_partial = Indicator.objects.filter(allows_partial=False).first()
        with self.assertRaises(ValueError):
            create_evidence(indicator=non_partial, submitted_by="tester", status="partially_met", payload={})
        physical = Indicator.objects.filter(category="physical").first()
        old = create_evidence(indicator=physical, submitted_by="tester", status="fully_met", payload={})
        old.submitted_at = timezone.now() - timedelta(days=800); old.save(update_fields=["submitted_at"])
        prune_old_evidence(); self.assertTrue(EvidenceRecord.objects.filter(pk=old.pk).exists())
        recurring_old = Indicator.objects.filter(category="recurring").exclude(frequency="as_needed").first()
        recurring_record = create_evidence(indicator=recurring_old, submitted_by="tester", status="fully_met", payload={}, period_label=period_label(recurring_old, date(2025, 1, 1)))
        recurring_record.submitted_at = timezone.now() - timedelta(days=800); recurring_record.save(update_fields=["submitted_at"])
        prune_old_evidence(); self.assertFalse(EvidenceRecord.objects.filter(pk=recurring_record.pk).exists())

    def test_drafting_gate(self):
        one_time = Indicator.objects.filter(category="one_time").first()
        draft = Draft.objects.create(indicator=one_time, kind="document", content="draft")
        self.assertEqual(draft.status, "draft")
        with self.assertRaises(ValueError): approve_draft(draft, "")
        approve_draft(draft, "reviewer")
        self.assertTrue(EvidenceRecord.objects.filter(indicator=one_time, is_current=True).exists())
        recurring_doc = Indicator.objects.filter(category="recurring", evidence_format="document").first()
        template = Draft.objects.create(indicator=recurring_doc, kind="template", content="template")
        approve_draft(template, "reviewer")
        self.assertFalse(EvidenceRecord.objects.filter(indicator=recurring_doc).exists())
        self.assertEqual(APIClient().get(f"/api/drafting/templates/{recurring_doc.pk}/").status_code, 200)
        rejected = Draft.objects.create(indicator=Indicator.objects.filter(category="one_time").exclude(pk=one_time.pk).first(), kind="document", content="secret", status="rejected")
        self.assertFalse(EvidenceRecord.objects.filter(payload__draft_id=rejected.id).exists())
        print_bytes = b"".join(APIClient().get("/api/exports/print-pack/").streaming_content)
        self.assertNotIn(b"secret", print_bytes)
        before = Draft.objects.count(); generate_bulk_drafts(); self.assertGreaterEqual(Draft.objects.count(), before)

    def test_stage_2_export_gate(self):
        response = APIClient().get("/api/exports/print-pack/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(b"".join(response.streaming_content).startswith(b"%PDF"))
