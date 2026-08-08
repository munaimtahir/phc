from django.db import models

from apps.registry.models import Indicator


def evidence_upload_path(instance, filename):
    return f"evidence/indicator_{instance.indicator_id}/{filename}"


class EvidenceRecord(models.Model):
    STATUS_CHOICES = [
        ("fully_met", "Fully met"),
        ("partially_met", "Partially met"),
        ("not_met", "Not met"),
    ]

    indicator = models.ForeignKey(Indicator, on_delete=models.PROTECT, related_name="evidence_records")
    period_label = models.CharField(max_length=16, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    submitted_by = models.CharField(max_length=255)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES)
    file = models.FileField(upload_to=evidence_upload_path, null=True, blank=True)
    structured_data = models.JSONField(default=dict, blank=True)
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["indicator", "period_label"]),
            models.Index(fields=["indicator", "is_current"]),
        ]

    def __str__(self):
        return f"Indicator #{self.indicator_id} — {self.period_label or 'n/a'} — {self.status}"
