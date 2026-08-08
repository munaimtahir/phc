import io
import re

from django.core.management import call_command
from django.test import TestCase
from pypdf import PdfReader

from apps.registry.models import Indicator
from apps.evidence.services import submit_evidence
from apps.exports.services import generate_print_pack_pdf
from apps.compliance.services import compliance_snapshot

INDICATOR_HEADER_RE = re.compile(r"#(\d+) \[")


def extract_text(pdf_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


class Stage2QualityGateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("load_indicators")

    def test_export_contains_exactly_118_indicators_no_dupes(self):
        pdf_bytes = generate_print_pack_pdf()
        text = extract_text(pdf_bytes)
        found_ids = [int(m.group(1)) for m in INDICATOR_HEADER_RE.finditer(text)]
        self.assertEqual(len(found_ids), 118)
        self.assertEqual(len(set(found_ids)), 118)

    def test_export_order_matches_source_id_sequence(self):
        pdf_bytes = generate_print_pack_pdf()
        text = extract_text(pdf_bytes)
        found_ids = [int(m.group(1)) for m in INDICATOR_HEADER_RE.finditer(text)]
        expected_ids = list(Indicator.objects.order_by("id").values_list("id", flat=True))
        self.assertEqual(found_ids, expected_ids)

    def test_indicator_with_no_evidence_still_appears_marked(self):
        pdf_bytes = generate_print_pack_pdf()
        text = extract_text(pdf_bytes)
        self.assertIn("No evidence submitted.", text)

    def test_compliance_percent_is_live_not_cached(self):
        pdf1 = generate_print_pack_pdf()
        text1 = extract_text(pdf1)
        pct_before = compliance_snapshot()["overall_pct"]

        submit_evidence(indicator=Indicator.objects.get(id=1), status="fully_met", submitted_by="t")
        submit_evidence(indicator=Indicator.objects.get(id=2), status="fully_met", submitted_by="t")
        submit_evidence(indicator=Indicator.objects.get(id=5), status="fully_met", submitted_by="t")

        pct_after = compliance_snapshot()["overall_pct"]
        self.assertNotAlmostEqual(pct_before, pct_after, places=2)

        pdf2 = generate_print_pack_pdf()
        text2 = extract_text(pdf2)

        self.assertIn(f"{pct_before:.2f}%", text1)
        self.assertIn(f"{pct_after:.2f}%", text2)
        self.assertNotIn(f"{pct_after:.2f}%", text1)

    def test_export_succeeds_end_to_end_single_action(self):
        pdf_bytes = generate_print_pack_pdf()
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
