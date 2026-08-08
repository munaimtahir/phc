from django.db import models


class Domain(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["code"]


class Standard(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name="standards")
    standard_no = models.CharField(max_length=20)
    code = models.CharField(max_length=20, unique=True)
    title = models.TextField()

    class Meta:
        ordering = ["domain__code", "standard_no"]
        constraints = [models.UniqueConstraint(fields=["domain", "standard_no"], name="unique_domain_standard")]


class Indicator(models.Model):
    CATEGORY_CHOICES = [(value, value) for value in ("physical", "one_time", "recurring")]
    FREQUENCY_CHOICES = [(value, value) for value in ("daily", "weekly", "monthly", "quarterly", "biannual", "annual", "as_needed")]
    EVIDENCE_FORMAT_CHOICES = [(value, value) for value in ("photo", "document", "structured_form")]

    standard = models.ForeignKey(Standard, on_delete=models.CASCADE, related_name="indicators")
    source_id = models.PositiveIntegerField(unique=True)
    text = models.TextField()
    weightage = models.PositiveSmallIntegerField(choices=((100, "100"), (80, "80")))
    allows_partial = models.BooleanField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, null=True, blank=True)
    evidence_format = models.CharField(max_length=20, choices=EVIDENCE_FORMAT_CHOICES)
    compliance_requirements = models.JSONField(default=list)
    survey_process = models.JSONField(default=list)
    retention_months = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["standard__domain__code", "standard__standard_no", "source_id"]


class LabProfile(models.Model):
    lab_name = models.CharField(max_length=255)
    address = models.TextField()
    phc_registration_no = models.CharField(max_length=100)
    supervising_pathologist = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lab profile"
