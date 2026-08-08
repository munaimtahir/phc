from django.core.exceptions import ValidationError
from django.db import models

from apps.registry.models import Indicator


class Draft(models.Model):
    KIND_CHOICES = [
        ("document", "Document"),
        ("template", "Template"),
    ]
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("pending_review", "Pending Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    indicators = models.ManyToManyField(Indicator, related_name="drafts", blank=True)
    indicator_ids = models.JSONField(default=list, blank=True)
    kind = models.CharField(max_length=16, choices=KIND_CHOICES, default="document")
    template_version = models.CharField(max_length=32, default="v1.0")

    prompt_text = models.TextField(default="", blank=True)
    raw_output = models.TextField(default="", blank=True)
    working_content = models.TextField(default="", blank=True)

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="draft")
    created_by = models.CharField(max_length=255, default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    reviewed_by = models.CharField(max_length=255, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    version_no = models.PositiveIntegerField(default=1)
    linked_document_id = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def content(self) -> str:
        return self.working_content

    @content.setter
    def content(self, value: str):
        self.working_content = value

    @property
    def indicator(self):
        if self.indicator_ids:
            return Indicator.objects.filter(id=self.indicator_ids[0]).first()
        return self.indicators.first()

    @property
    def indicator_id(self):
        if self.indicator_ids:
            return self.indicator_ids[0]
        first_ind = self.indicators.first()
        return first_ind.id if first_ind else None

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old = Draft.objects.get(pk=self.pk)
                if old.prompt_text and self.prompt_text != old.prompt_text:
                    raise ValidationError("prompt_text is immutable once created.")
                if old.raw_output and self.raw_output != old.raw_output:
                    raise ValidationError("raw_output is immutable once saved.")
            except Draft.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Draft #{self.id} ({self.kind}) indicators {self.indicator_ids} [{self.status}]"
