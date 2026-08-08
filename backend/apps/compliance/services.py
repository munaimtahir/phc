from apps.registry.models import Indicator
from apps.evidence.models import EvidenceRecord

STATUS_MULTIPLIER = {
    "fully_met": 1.0,
    "partially_met": 0.8,
    "not_met": 0.0,
}


def indicator_snapshot(indicator: Indicator) -> dict:
    """Most recent EvidenceRecord for this indicator (any period), not
    necessarily the current period's."""
    latest = (
        EvidenceRecord.objects.filter(indicator=indicator)
        .order_by("-submitted_at")
        .first()
    )
    if latest is None:
        status = None
        earned = 0.0
    else:
        status = latest.status
        multiplier = STATUS_MULTIPLIER[status]
        if status == "partially_met" and not indicator.allows_partial:
            multiplier = 0.0
        earned = indicator.weightage * multiplier
    return {
        "indicator": indicator,
        "latest_record": latest,
        "status": status,
        "earned_weightage": earned,
        "possible_weightage": indicator.weightage,
    }


def compliance_snapshot() -> dict:
    indicators = Indicator.objects.all()
    per_indicator = [indicator_snapshot(ind) for ind in indicators]
    earned_total = sum(row["earned_weightage"] for row in per_indicator)
    possible_total = sum(row["possible_weightage"] for row in per_indicator)
    overall_pct = (earned_total / possible_total * 100) if possible_total else 0.0
    return {
        "per_indicator": per_indicator,
        "earned_total": earned_total,
        "possible_total": possible_total,
        "overall_pct": overall_pct,
    }
