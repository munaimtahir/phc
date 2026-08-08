import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from apps.registry.models import Indicator
from apps.evidence.models import EvidenceRecord
from apps.evidence.services import due_list, submit_evidence, prune_expired_evidence
from apps.compliance.services import compliance_snapshot


class Stage1QualityGateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("load_indicators")

    def test_due_list_hand_built_fixture(self):
        test_date = datetime.date(2026, 8, 2)  # a Sunday
        # #6 is daily -> due, no record yet -> should appear as not done
        # #43 is monthly -> submit for this month -> should appear as done
        submit_evidence(
            indicator=Indicator.objects.get(id=43),
            status="fully_met",
            submitted_by="tester",
            on_date=test_date,
        )
        rows = {row["indicator"].id: row for row in due_list(test_date)}

        self.assertIn(6, rows)
        self.assertFalse(rows[6]["done"])
        self.assertEqual(rows[6]["period_label"], "2026-08-02")

        self.assertIn(43, rows)
        self.assertTrue(rows[43]["done"])
        self.assertEqual(rows[43]["period_label"], "2026-08")

    def test_physical_and_one_time_never_on_due_list(self):
        rows = due_list(datetime.date(2026, 8, 2))
        ids = {row["indicator"].id for row in rows}
        physical_and_one_time_ids = set(
            Indicator.objects.filter(category__in=["physical", "one_time"]).values_list("id", flat=True)
        )
        self.assertEqual(ids & physical_and_one_time_ids, set())

    def test_as_needed_never_on_due_list_even_with_history(self):
        indicator = Indicator.objects.get(id=30)  # as_needed
        self.assertEqual(indicator.frequency, "as_needed")
        submit_evidence(indicator=indicator, status="fully_met", submitted_by="tester")
        submit_evidence(indicator=indicator, status="fully_met", submitted_by="tester")
        rows = due_list(datetime.date(2026, 8, 2))
        ids = {row["indicator"].id for row in rows}
        self.assertNotIn(30, ids)

    def test_partially_met_rejected_when_not_allowed(self):
        indicator = Indicator.objects.get(id=6)  # allows_partial=False
        self.assertFalse(indicator.allows_partial)
        with self.assertRaises(ValidationError):
            submit_evidence(indicator=indicator, status="partially_met", submitted_by="tester")

    def test_partially_met_accepted_when_allowed(self):
        indicator = Indicator.objects.get(id=3)  # allows_partial=True, physical
        record = submit_evidence(indicator=indicator, status="partially_met", submitted_by="tester")
        self.assertEqual(record.status, "partially_met")

    def test_no_recurring_non_as_needed_record_with_null_period_label(self):
        submit_evidence(indicator=Indicator.objects.get(id=43), status="fully_met", submitted_by="t")
        submit_evidence(indicator=Indicator.objects.get(id=13), status="fully_met", submitted_by="t")  # annual
        bad = EvidenceRecord.objects.filter(
            indicator__category="recurring",
            period_label__isnull=True,
        ).exclude(indicator__frequency="as_needed")
        self.assertEqual(bad.count(), 0)

    def test_retention_prunes_old_recurring_but_never_current_one_time(self):
        recurring = Indicator.objects.get(id=43)  # monthly, retention 12 months
        old_record = submit_evidence(
            indicator=recurring, status="fully_met", submitted_by="t",
            on_date=datetime.date(2020, 1, 15),
        )
        EvidenceRecord.objects.filter(id=old_record.id).update(
            submitted_at=datetime.datetime(2020, 1, 15, tzinfo=datetime.timezone.utc)
        )
        one_time = Indicator.objects.get(id=5)
        old_one_time_record = submit_evidence(
            indicator=one_time, status="fully_met", submitted_by="t",
        )
        EvidenceRecord.objects.filter(id=old_one_time_record.id).update(
            submitted_at=datetime.datetime(2015, 1, 1, tzinfo=datetime.timezone.utc)
        )

        deleted = prune_expired_evidence(today=datetime.date(2026, 8, 2))
        self.assertGreaterEqual(deleted, 1)
        self.assertFalse(EvidenceRecord.objects.filter(id=old_record.id).exists())
        self.assertTrue(EvidenceRecord.objects.filter(id=old_one_time_record.id, is_current=True).exists())

    def test_compliance_fixture_hand_calculated(self):
        # Build a known set across >=10 indicators, all three statuses.
        fully_met_100 = [1, 2, 5]          # weightage 100 each -> 300
        partially_met_ids = [4, 7]           # allows_partial True, weightage 80 -> 0.8*80 each
        not_met_ids = [8, 9, 10]             # explicit not_met -> 0
        no_record_ids = [11, 12]             # no record -> 0

        for iid in fully_met_100:
            submit_evidence(indicator=Indicator.objects.get(id=iid), status="fully_met", submitted_by="t")
        for iid in partially_met_ids:
            submit_evidence(indicator=Indicator.objects.get(id=iid), status="partially_met", submitted_by="t")
        for iid in not_met_ids:
            submit_evidence(indicator=Indicator.objects.get(id=iid), status="not_met", submitted_by="t")

        touched_ids = fully_met_100 + partially_met_ids + not_met_ids + no_record_ids
        snap = compliance_snapshot()
        by_id = {row["indicator"].id: row for row in snap["per_indicator"]}

        expected_earned = 0.0
        expected_possible = 0.0
        for iid in touched_ids:
            row = by_id[iid]
            expected_possible += row["indicator"].weightage
            if iid in fully_met_100:
                expected_earned += row["indicator"].weightage
            elif iid in partially_met_ids:
                expected_earned += row["indicator"].weightage * 0.8
            # not_met / no_record contribute 0

        overall_touched_earned = sum(by_id[i]["earned_weightage"] for i in touched_ids)
        overall_touched_possible = sum(by_id[i]["possible_weightage"] for i in touched_ids)
        self.assertAlmostEqual(overall_touched_earned, expected_earned, places=2)
        self.assertAlmostEqual(overall_touched_possible, expected_possible, places=2)

        # sanity: overall % across all 118 must be earned/possible of the whole registry
        all_possible = sum(row["possible_weightage"] for row in snap["per_indicator"])
        all_earned = sum(row["earned_weightage"] for row in snap["per_indicator"])
        self.assertAlmostEqual(snap["overall_pct"], all_earned / all_possible * 100, places=6)

    def test_uses_most_recent_record_not_current_period(self):
        indicator = Indicator.objects.get(id=43)  # monthly
        submit_evidence(
            indicator=indicator, status="not_met", submitted_by="t",
            on_date=datetime.date(2026, 1, 5),
        )
        submit_evidence(
            indicator=indicator, status="fully_met", submitted_by="t",
            on_date=datetime.date(2026, 7, 5),
        )
        snap = compliance_snapshot()
        row = next(r for r in snap["per_indicator"] if r["indicator"].id == 43)
        self.assertEqual(row["status"], "fully_met")

    def test_entry_form_input_type_per_evidence_format(self):
        user = User.objects.create_user(username="staff1", password="pw")
        client = APIClient()
        client.force_authenticate(user=user)

        # photo indicator -> file upload accepted
        photo_file = SimpleUploadedFile("sign.jpg", b"fakeimg", content_type="image/jpeg")
        resp = client.post("/api/evidence/submit/", {
            "indicator": 1, "status": "fully_met", "file": photo_file,
        }, format="multipart")
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.json()["file"])

        # document indicator -> file upload accepted
        doc_file = SimpleUploadedFile("policy.pdf", b"fakepdf", content_type="application/pdf")
        resp = client.post("/api/evidence/submit/", {
            "indicator": 4, "status": "fully_met", "file": doc_file,
        }, format="multipart")
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.json()["file"])

        # structured_form indicator -> digital fields, schema exposes field defs
        schema_resp = client.get("/api/evidence/structured-form-schema/53/")
        self.assertEqual(schema_resp.status_code, 200)
        field_names = {f["name"] for f in schema_resp.json()["fields"]}
        self.assertIn("equipment_name", field_names)

        resp = client.post("/api/evidence/submit/", {
            "indicator": 53,
            "status": "fully_met",
            "equipment_name": "Centrifuge",
            "date_of_purchase": "2024-01-01",
            "source": "ACME Corp",
            "date_of_commissioning": "2024-01-15",
        })
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["structured_data"]["equipment_name"], "Centrifuge")

        # missing a required structured field is rejected
        resp = client.post("/api/evidence/submit/", {
            "indicator": 53, "status": "fully_met",
        })
        self.assertEqual(resp.status_code, 400)
