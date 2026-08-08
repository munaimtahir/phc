from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.registry.models import Indicator, LabProfile
from apps.evidence.models import EvidenceRecord
from apps.evidence.services import submit_evidence
from .models import Draft

DOCUMENTARY_FORMATS = {"document", "structured_form"}
REQUIRED_HEADERS = [
    "Purpose",
    "Scope",
    "Roles & responsibilities",
    "Procedure",
    "Records & evidence",
    "References",
]


def draft_kind_for_indicators(indicators: list[Indicator]) -> str:
    if any(ind.category == "one_time" for ind in indicators):
        return "document"
    if all(ind.category == "recurring" and ind.evidence_format in DOCUMENTARY_FORMATS for ind in indicators):
        return "template"
    return "document"


def eligible_indicators() -> list[Indicator]:
    return [
        ind for ind in Indicator.objects.all()
        if ind.category == "one_time" or (ind.category == "recurring" and ind.evidence_format in DOCUMENTARY_FORMATS)
    ]


def _has_current_evidence(indicator: Indicator) -> bool:
    if indicator.category == "one_time":
        return EvidenceRecord.objects.filter(indicator=indicator, is_current=True).exists()
    if indicator.category == "recurring":
        return Draft.objects.filter(
            indicator_ids__contains=[indicator.id], kind="template", status="approved"
        ).exists()
    return False


def build_prompt(indicators: list[Indicator], existing_draft: Draft | None = None) -> str:
    if not indicators:
        raise ValidationError("At least one indicator must be selected to generate a prompt.")

    profile = LabProfile.load()
    kind = draft_kind_for_indicators(indicators)

    lab_block = (
        f"Laboratory Name: {profile.lab_name}\n"
        f"Address: {profile.address}\n"
        f"PHC Registration No.: {profile.phc_registration_no}\n"
        f"Supervising Pathologist: {profile.supervising_pathologist}\n"
    )

    indicators_block_list = []
    for ind in indicators:
        reqs = "\n".join(f"  - {r}" for r in ind.compliance_requirements)
        survey = "\n".join(f"  - {s}" for s in ind.survey_process)
        indicators_block_list.append(
            f"--- Indicator #{ind.id} ---\n"
            f"Title: {ind.text}\n"
            f"Category: {ind.category} | Format: {ind.evidence_format}\n"
            f"Compliance Requirements:\n{reqs}\n"
            f"Survey Process (Assessor Checks):\n{survey}\n"
        )
    indicators_block = "\n".join(indicators_block_list)

    headers_instruction = (
        "OUTPUT FORMAT CONTRACT:\n"
        "You MUST structure your entire document in Markdown using the following fixed section headers, in this exact order:\n\n"
        "1. # Purpose\n"
        "2. # Scope\n"
        "3. # Roles & responsibilities\n"
        "4. # Procedure\n"
        "5. # Records & evidence\n"
        "6. # References\n"
    )

    if kind == "document":
        task_instruction = (
            "TASK: Draft a complete, official SOP / Policy Document ready for filing as compliance evidence.\n"
            "Name the laboratory and its details explicitly throughout the text."
        )
    else:
        task_instruction = (
            "TASK: Draft a reusable template structure/format that staff will fill in each period.\n"
            "It should capture all required monitoring parameters and survey checks."
        )

    revision_block = ""
    if existing_draft and existing_draft.working_content:
        revision_block = (
            "\n=== EXISTING APPROVED DOCUMENT (REVISION MODE) ===\n"
            "Below is the current approved document. Please revise and update it to address "
            "the selected indicator requirements rather than starting from scratch:\n\n"
            f"{existing_draft.working_content}\n"
            "===================================================\n\n"
        )

    return (
        f"=== LAB PROFILE ===\n{lab_block}\n"
        f"=== TARGET INDICATOR(S) ===\n{indicators_block}\n"
        f"{revision_block}"
        f"{task_instruction}\n\n"
        f"{headers_instruction}"
    )


def create_prompt_draft(
    indicator_ids: list[int],
    created_by: str = "",
    existing_draft_id: int | None = None,
) -> Draft:
    if not indicator_ids:
        raise ValidationError("indicator_ids list cannot be empty.")

    indicators = list(Indicator.objects.filter(id__in=indicator_ids))
    if not indicators:
        raise ValidationError("No valid indicators found for the provided IDs.")

    existing_draft = None
    linked_doc_id = None
    version_no = 1

    if existing_draft_id:
        existing_draft = Draft.objects.filter(id=existing_draft_id).first()
        if existing_draft:
            linked_doc_id = existing_draft.id
            version_no = existing_draft.version_no + 1

    kind = draft_kind_for_indicators(indicators)
    prompt_text = build_prompt(indicators, existing_draft=existing_draft)

    draft = Draft.objects.create(
        indicator_ids=[ind.id for ind in indicators],
        kind=kind,
        prompt_text=prompt_text,
        status="draft",
        created_by=created_by,
        version_no=version_no,
        linked_document_id=linked_doc_id,
    )
    draft.indicators.set(indicators)
    return draft


def save_raw_output(draft: Draft, raw_output: str) -> Draft:
    if not raw_output or not raw_output.strip():
        raise ValidationError("raw_output cannot be empty.")

    if draft.raw_output and draft.raw_output != raw_output:
        raise ValidationError("raw_output is immutable once saved.")

    draft.raw_output = raw_output
    draft.working_content = raw_output  # Seed working content
    draft.status = "pending_review"
    draft.save(update_fields=["raw_output", "working_content", "status"])
    return draft


def update_working_content(draft: Draft, working_content: str) -> Draft:
    draft.working_content = working_content
    draft.save(update_fields=["working_content"])
    return draft


@transaction.atomic
def approve_draft(draft: Draft, reviewed_by: str) -> Draft:
    if not reviewed_by or not reviewed_by.strip():
        raise ValidationError("reviewed_by is required to approve a draft.")
    if draft.status not in ("draft", "pending_review"):
        raise ValidationError(f"Draft #{draft.id} is already {draft.status}.")

    draft.status = "approved"
    draft.reviewed_by = reviewed_by
    draft.reviewed_at = timezone.now()
    draft.save(update_fields=["status", "reviewed_by", "reviewed_at"])

    if draft.kind == "document":
        for ind_id in draft.indicator_ids:
            indicator = Indicator.objects.filter(id=ind_id).first()
            if indicator:
                submit_evidence(
                    indicator=indicator,
                    status="fully_met",
                    submitted_by=f"AI draft approved by {reviewed_by}",
                    structured_data={
                        "source": "ai_draft",
                        "draft_id": draft.id,
                        "content": draft.working_content,
                    },
                )
    # Template drafts never create/modify an EvidenceRecord

    return draft


@transaction.atomic
def reject_draft(draft: Draft, reviewed_by: str) -> Draft:
    if not reviewed_by or not reviewed_by.strip():
        raise ValidationError("reviewed_by is required to reject a draft.")
    if draft.status not in ("draft", "pending_review"):
        raise ValidationError(f"Draft #{draft.id} is already {draft.status}.")

    draft.status = "rejected"
    draft.reviewed_by = reviewed_by
    draft.reviewed_at = timezone.now()
    draft.save(update_fields=["status", "reviewed_by", "reviewed_at"])
    return draft
