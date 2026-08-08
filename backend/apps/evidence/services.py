from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from apps.registry.models import Indicator
from .models import EvidenceRecord


def period_label(indicator, on_date):
    frequency = indicator.frequency
    if frequency == "daily":
        return on_date.strftime("%Y-%m-%d")
    if frequency == "weekly":
        iso = on_date.isocalendar()
        return f"{iso.year}-W{iso.week:02d}"
    if frequency == "monthly":
        return on_date.strftime("%Y-%m")
    if frequency == "quarterly":
        return f"{on_date.year}-Q{((on_date.month - 1) // 3) + 1}"
    if frequency == "biannual":
        return f"{on_date.year}-H{1 if on_date.month <= 6 else 2}"
    if frequency == "annual":
        return str(on_date.year)
    return None


@transaction.atomic
def create_evidence(*, indicator, submitted_by, status, payload, period_label=None, attachment=None):
    if status == "partially_met" and not indicator.allows_partial:
        raise ValueError("partially_met is not allowed for this indicator")
    recurring = indicator.category == "recurring"
    if recurring and indicator.frequency != "as_needed" and period_label is None:
        raise ValueError("period_label is required for recurring non_as_needed evidence")
    if not recurring and period_label is not None:
        raise ValueError("period_label is only valid for recurring evidence")
    if recurring:
        EvidenceRecord.objects.filter(indicator=indicator, period_label=period_label).update(is_current=False)
    else:
        EvidenceRecord.objects.filter(indicator=indicator, is_current=True).update(is_current=False)
    return EvidenceRecord.objects.create(indicator=indicator, period_label=period_label, submitted_by=submitted_by,
                                         status=status, payload=payload, attachment=attachment, is_current=True)


def due_list(on_date=None):
    on_date = on_date or timezone.localdate()
    result = []
    for indicator in Indicator.objects.filter(category="recurring").exclude(frequency="as_needed").select_related("standard__domain"):
        label = period_label(indicator, on_date)
        result.append({"indicator": indicator, "period_label": label,
                       "has_evidence": EvidenceRecord.objects.filter(indicator=indicator, period_label=label).exists()})
    return result


def prune_old_evidence(now=None):
    now = now or timezone.now()
    deleted = 0
    for record in EvidenceRecord.objects.filter(indicator__category="recurring").exclude(indicator__frequency="as_needed").select_related("indicator"):
        months = record.indicator.retention_months or 12
        if record.submitted_at < now - timedelta(days=30 * months):
            record.delete()
            deleted += 1
    return (deleted, {})


def compliance_summary():
    possible = sum(i.weightage for i in Indicator.objects.all())
    earned = 0
    for indicator in Indicator.objects.all():
        record = indicator.evidence_records.order_by("-submitted_at", "-id").first()
        if record and record.status == "fully_met":
            earned += indicator.weightage
        elif record and record.status == "partially_met" and indicator.allows_partial:
            earned += indicator.weightage * 0.8
    return {"earned_weightage": earned, "possible_weightage": possible,
            "compliance_percent": round((earned / possible * 100) if possible else 0, 2)}
