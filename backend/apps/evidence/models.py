from django.db import models
from apps.registry.models import Indicator


class EvidenceRecord(models.Model):
    STATUS_CHOICES = [(value, value) for value in ("fully_met", "partially_met", "not_met")]
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name="evidence_records")
    period_label = models.CharField(max_length=20, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    submitted_by = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    payload = models.JSONField(default=dict)
    attachment = models.FileField(upload_to="evidence/%Y/%m", null=True, blank=True)
    is_current = models.BooleanField(default=True)

    class Meta:
        ordering = ["-submitted_at", "-id"]
        constraints = [models.UniqueConstraint(fields=["indicator", "period_label"], name="unique_evidence_period")]
