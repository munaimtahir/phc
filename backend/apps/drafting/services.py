import os
from django.utils import timezone
from apps.evidence.services import create_evidence
from apps.registry.models import Indicator, LabProfile
from .models import Draft


def eligible_kind(indicator):
    if indicator.category == "one_time":
        return "document"
    if indicator.category == "recurring" and indicator.evidence_format == "document":
        return "template"
    return None


def approve_draft(draft, reviewed_by):
    if not reviewed_by:
        raise ValueError("reviewed_by is required")
    draft.status, draft.reviewed_by, draft.reviewed_at = "approved", reviewed_by, timezone.now()
    draft.save(update_fields=["status", "reviewed_by", "reviewed_at"])
    if draft.kind == "document":
        create_evidence(indicator=draft.indicator, submitted_by=reviewed_by, status="fully_met",
                        payload={"draft_id": draft.id, "content": draft.content})
    return draft


def generate_content(indicator):
    lab = LabProfile.objects.first()
    grounded = (f"Indicator: {indicator.text}\n\nInstitution: {lab.lab_name}\nAddress: {lab.address}\n"
            f"PHC Registration: {lab.phc_registration_no}\nSupervising Pathologist: {lab.supervising_pathologist}\n\n"
            "Compliance requirements:\n- " + "\n- ".join(indicator.compliance_requirements) +
            "\n\nSurvey process:\n- " + "\n- ".join(indicator.survey_process))
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return grounded
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
        max_tokens=4000,
        system="Draft a professional laboratory compliance document grounded only in the supplied PHC requirements and lab profile.",
        messages=[{"role": "user", "content": grounded}],
    )
    return "\n".join(block.text for block in response.content if hasattr(block, "text"))


def generate_bulk_drafts():
    created = []
    for indicator in Indicator.objects.all().prefetch_related("evidence_records"):
        kind = eligible_kind(indicator)
        if kind and not indicator.evidence_records.filter(is_current=True).exists():
            created.append(Draft.objects.create(indicator=indicator, kind=kind, content=generate_content(indicator)))
    return created
