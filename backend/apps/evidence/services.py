import datetime

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.registry.models import Indicator
from .models import EvidenceRecord


def current_period_label(frequency: str, on_date: datetime.date) -> str | None:
    """Compute the period_label for a recurring frequency at a given date.

    as_needed indicators are event-triggered, not period-keyed -> None.
    """
    if frequency == "daily":
        return on_date.strftime("%Y-%m-%d")
    if frequency == "weekly":
        iso_year, iso_week, _ = on_date.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"
    if frequency == "monthly":
        return on_date.strftime("%Y-%m")
    if frequency == "quarterly":
        quarter = (on_date.month - 1) // 3 + 1
        return f"{on_date.year}-Q{quarter}"
    if frequency == "biannual":
        half = 1 if on_date.month <= 6 else 2
        return f"{on_date.year}-H{half}"
    if frequency == "annual":
        return str(on_date.year)
    if frequency == "as_needed":
        return None
    raise ValueError(f"Unknown frequency: {frequency}")


def due_list(on_date: datetime.date):
    """Recurring (non-as_needed) indicators, with whether the current period
    already has an EvidenceRecord. Presence-only, no deadline/lateness logic.
    """
    indicators = Indicator.objects.filter(category="recurring").exclude(frequency="as_needed")
    results = []
    for indicator in indicators:
        period_label = current_period_label(indicator.frequency, on_date)
        has_record = EvidenceRecord.objects.filter(
            indicator=indicator, period_label=period_label
        ).exists()
        results.append({
            "indicator": indicator,
            "period_label": period_label,
            "done": has_record,
        })
    return results


@transaction.atomic
def submit_evidence(
    *,
    indicator: Indicator,
    status: str,
    submitted_by: str,
    file=None,
    structured_data: dict | None = None,
    on_date: datetime.date | None = None,
) -> EvidenceRecord:
    if status == "partially_met" and not indicator.allows_partial:
        raise ValidationError(
            f"Indicator #{indicator.id} does not allow 'partially_met' status."
        )
    if status not in dict(EvidenceRecord.STATUS_CHOICES):
        raise ValidationError(f"Invalid status: {status}")

    on_date = on_date or datetime.date.today()
    structured_data = structured_data or {}

    if indicator.category in ("physical", "one_time"):
        EvidenceRecord.objects.filter(indicator=indicator, is_current=True).update(is_current=False)
        record = EvidenceRecord.objects.create(
            indicator=indicator,
            period_label=None,
            submitted_by=submitted_by,
            status=status,
            file=file,
            structured_data=structured_data,
            is_current=True,
        )
        return record

    # recurring
    if indicator.frequency == "as_needed":
        # event-triggered: every submission is its own occurrence, never
        # updated in place, never period-keyed, never on the due-list.
        return EvidenceRecord.objects.create(
            indicator=indicator,
            period_label=None,
            submitted_by=submitted_by,
            status=status,
            file=file,
            structured_data=structured_data,
            is_current=False,
        )

    period_label = current_period_label(indicator.frequency, on_date)
    record, _created = EvidenceRecord.objects.update_or_create(
        indicator=indicator,
        period_label=period_label,
        defaults={
            "submitted_by": submitted_by,
            "status": status,
            "file": file,
            "structured_data": structured_data,
            "is_current": False,
        },
    )
    return record


def prune_expired_evidence(today: datetime.date | None = None) -> int:
    """Delete recurring EvidenceRecords older than their indicator's
    retention_months. Physical/one-time current records are never pruned.
    """
    today = today or datetime.date.today()
    deleted_count = 0
    recurring_indicators = Indicator.objects.filter(category="recurring").exclude(
        retention_months__isnull=True
    )
    for indicator in recurring_indicators:
        cutoff = today - datetime.timedelta(days=indicator.retention_months * 30)
        qs = EvidenceRecord.objects.filter(
            indicator=indicator,
            submitted_at__date__lt=cutoff,
        )
        deleted_count += qs.count()
        qs.delete()
    return deleted_count
