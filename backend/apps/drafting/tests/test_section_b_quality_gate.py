import io
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from pypdf import PdfReader

from apps.registry.models import Indicator
from apps.evidence.models import EvidenceRecord
from apps.evidence.services import submit_evidence
from apps.exports.services import generate_print_pack_pdf
from apps.compliance.services import compliance_snapshot
from .. import services
from ..models import Draft


def extract_text(pdf_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


class SectionBRedesignQualityGateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("load_indicators")

    def test_prompt_builder_single_indicator(self):
        ind = Indicator.objects.filter(category="one_time").first()
        draft = services.create_prompt_draft(indicator_ids=[ind.id], created_by="staff1")
        self.assertIsNotNone(draft.prompt_text)
        self.assertIn(f"Indicator #{ind.id}", draft.prompt_text)
        self.assertIn(ind.text, draft.prompt_text)
        self.assertEqual(draft.status, "draft")

    def test_prompt_builder_multiple_indicators(self):
        inds = list(Indicator.objects.filter(category="one_time")[:3])
        ind_ids = [i.id for i in inds]
        draft = services.create_prompt_draft(indicator_ids=ind_ids, created_by="staff1")
        self.assertEqual(draft.indicator_ids, ind_ids)
        for ind in inds:
            self.assertIn(f"Indicator #{ind.id}", draft.prompt_text)

    def test_prompt_text_contains_lab_profile_requirements_and_fixed_headers(self):
        ind = Indicator.objects.filter(category="one_time").first()
        prompt = services.build_prompt([ind])

        # Lab profile verification
        self.assertIn("Al Shifa Laboratory", prompt)
        self.assertIn("Circular Road, Jaranwala", prompt)
        self.assertIn("P-20787", prompt)
        self.assertIn("Dr. Mubashr Ahmed", prompt)

        # Requirements and survey process
        self.assertIn(ind.text, prompt)

        # Fixed Markdown headers contract
        self.assertIn("Purpose", prompt)
        self.assertIn("Scope", prompt)
        self.assertIn("Roles & responsibilities", prompt)
        self.assertIn("Procedure", prompt)
        self.assertIn("Records & evidence", prompt)
        self.assertIn("References", prompt)

    def test_output_receiver_saves_raw_output_and_seeds_working_content(self):
        ind = Indicator.objects.filter(category="one_time").first()
        draft = services.create_prompt_draft(indicator_ids=[ind.id])

        sample_output = "# Purpose\nTest purpose.\n# Scope\nTest scope."
        updated = services.save_raw_output(draft, sample_output)

        self.assertEqual(updated.raw_output, sample_output)
        self.assertEqual(updated.working_content, sample_output)
        self.assertEqual(updated.status, "pending_review")

    def test_editing_working_content_never_mutates_raw_output_or_prompt_text(self):
        ind = Indicator.objects.filter(category="one_time").first()
        draft = services.create_prompt_draft(indicator_ids=[ind.id])
        initial_prompt = draft.prompt_text

        raw_text = "# Purpose\nRaw AI response."
        services.save_raw_output(draft, raw_text)

        # Edit working content
        edited_text = "# Purpose\nEdited human response."
        services.update_working_content(draft, edited_text)

        draft.refresh_from_db()
        self.assertEqual(draft.prompt_text, initial_prompt)
        self.assertEqual(draft.raw_output, raw_text)
        self.assertEqual(draft.working_content, edited_text)

        # Direct mutation attempt on immutable fields fails
        draft.prompt_text = "Mutated prompt"
        with self.assertRaises(ValidationError):
            draft.save()

    def test_draft_and_rejected_drafts_never_readable_from_evidence_or_print_path(self):
        one_time = Indicator.objects.filter(category="one_time").first()
        recurring_doc = Indicator.objects.filter(
            category="recurring", evidence_format__in=["document", "structured_form"]
        ).first()

        draft1 = services.create_prompt_draft(indicator_ids=[one_time.id])
        services.save_raw_output(draft1, "# Purpose\nDraft 1 text")

        draft2 = services.create_prompt_draft(indicator_ids=[recurring_doc.id])
        services.save_raw_output(draft2, "# Purpose\nDraft 2 text")
        services.reject_draft(draft2, reviewed_by="reviewer1")

        self.assertFalse(EvidenceRecord.objects.filter(indicator=one_time).exists())
        self.assertFalse(EvidenceRecord.objects.filter(indicator=recurring_doc).exists())

        text = extract_text(generate_print_pack_pdf())
        self.assertNotIn("Draft 1 text", text)
        self.assertNotIn("Draft 2 text", text)

    def test_approving_document_draft_becomes_current_evidence_and_supersedes(self):
        one_time = Indicator.objects.filter(category="one_time").first()
        old_record = submit_evidence(indicator=one_time, status="not_met", submitted_by="staff")
        self.assertTrue(EvidenceRecord.objects.get(id=old_record.id).is_current)

        draft = services.create_prompt_draft(indicator_ids=[one_time.id])
        services.save_raw_output(draft, "# Purpose\nApproved document content")
        services.approve_draft(draft, reviewed_by="Dr. Mubashr Ahmed")

        old_record.refresh_from_db()
        self.assertFalse(old_record.is_current)

        current = EvidenceRecord.objects.get(indicator=one_time, is_current=True)
        self.assertEqual(current.status, "fully_met")
        self.assertEqual(current.structured_data["draft_id"], draft.id)
        self.assertIn("Approved document content", current.structured_data["content"])

    def test_approving_template_draft_does_not_touch_evidence_records(self):
        recurring_doc = Indicator.objects.filter(
            category="recurring", evidence_format__in=["document", "structured_form"]
        ).first()

        before_count = EvidenceRecord.objects.count()
        draft = services.create_prompt_draft(indicator_ids=[recurring_doc.id])
        self.assertEqual(draft.kind, "template")

        services.save_raw_output(draft, "# Purpose\nTemplate structure")
        services.approve_draft(draft, reviewed_by="reviewer1")

        self.assertEqual(EvidenceRecord.objects.count(), before_count)
        self.assertEqual(Draft.objects.get(id=draft.id).status, "approved")

    def test_approve_without_reviewed_by_is_rejected(self):
        one_time = Indicator.objects.filter(category="one_time").first()
        draft = services.create_prompt_draft(indicator_ids=[one_time.id])
        services.save_raw_output(draft, "# Purpose\nSample output")

        with self.assertRaises(ValidationError):
            services.approve_draft(draft, reviewed_by="")

        draft.refresh_from_db()
        self.assertEqual(draft.status, "pending_review")

    def test_no_anthropic_sdk_or_api_key_used(self):
        self.assertFalse(hasattr(services, "anthropic"))
