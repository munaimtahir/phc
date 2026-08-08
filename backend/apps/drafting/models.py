from django.db import models
from apps.registry.models import Indicator


class Draft(models.Model):
    KIND_CHOICES = [("document", "document"), ("template", "template")]
    STATUS_CHOICES = [(value, value) for value in ("draft", "approved", "rejected")]
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name="drafts")
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    content = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    reviewed_by = models.CharField(max_length=255, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    version_no = models.PositiveIntegerField(default=1)
