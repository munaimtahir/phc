from django.db import models


class Domain(models.Model):
    code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.code} — {self.name}"


class Standard(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.PROTECT, related_name="standards")
    standard_no = models.CharField(max_length=16)
    code = models.CharField(max_length=32, unique=True)
    title = models.CharField(max_length=1000)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.code} — {self.title}"


class Indicator(models.Model):
    CATEGORY_CHOICES = [
        ("physical", "Physical"),
        ("one_time", "One-time"),
        ("recurring", "Recurring"),
    ]
    FREQUENCY_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("biannual", "Biannual"),
        ("annual", "Annual"),
        ("as_needed", "As needed"),
    ]
    EVIDENCE_FORMAT_CHOICES = [
        ("photo", "Photo"),
        ("document", "Document"),
        ("structured_form", "Structured form"),
    ]

    id = models.PositiveIntegerField(primary_key=True)
    standard = models.ForeignKey(Standard, on_delete=models.PROTECT, related_name="indicators")
    text = models.TextField()
    weightage = models.PositiveSmallIntegerField()
    allows_partial = models.BooleanField(default=False)
    category = models.CharField(max_length=16, choices=CATEGORY_CHOICES)
    frequency = models.CharField(max_length=16, choices=FREQUENCY_CHOICES, null=True, blank=True)
    evidence_format = models.CharField(max_length=32, choices=EVIDENCE_FORMAT_CHOICES)
    compliance_requirements = models.JSONField(default=list)
    survey_process = models.JSONField(default=list)
    scoring = models.JSONField(default=list)
    guidelines = models.JSONField(default=list)
    retention_months = models.PositiveSmallIntegerField(null=True, blank=True)
    classification_source = models.CharField(max_length=32, blank=True)
    classification_note = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"#{self.id} {self.text[:60]}"


class LabProfile(models.Model):
    lab_name = models.CharField(max_length=255)
    address = models.CharField(max_length=500)
    phc_registration_no = models.CharField(max_length=64)
    supervising_pathologist = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Lab Profile"
        verbose_name_plural = "Lab Profile"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.lab_name
