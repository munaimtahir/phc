from django.db import models
from django.conf import settings

class Indicator(models.Model):
    indicator_no = models.CharField(max_length=50, unique=True)
    functional_area_code = models.CharField(max_length=50, blank=True)
    functional_area_name = models.CharField(max_length=255, blank=True)
    standard_no = models.CharField(max_length=50, blank=True)
    standard_code = models.CharField(max_length=50, blank=True)
    standard_title = models.CharField(max_length=255, blank=True)
    indicator_text = models.TextField()
    
    max_score = models.IntegerField(default=10)
    weightage_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    compliance_requirement = models.TextField(blank=True)
    surveyor_check = models.TextField(blank=True)
    required_evidence = models.TextField(blank=True)
    evidence_category = models.CharField(max_length=100, blank=True)
    
    register_required = models.BooleanField(default=False)
    register_name = models.CharField(max_length=255, blank=True)
    
    recurring_required = models.BooleanField(default=False)
    recurrence_frequency = models.CharField(max_length=50, blank=True)
    
    document_to_generate = models.CharField(max_length=255, blank=True)
    physical_action_required = models.BooleanField(default=False)
    
    is_locked = models.BooleanField(default=True)
    source_reference = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.indicator_no} - {self.indicator_text[:50]}"

class IndicatorCompliance(models.Model):
    EVIDENCE_STATUS_CHOICES = [
        ('missing', 'Missing'),
        ('partial', 'Partial'),
        ('ready', 'Ready'),
        ('verified', 'Verified'),
        ('not_applicable', 'Not Applicable'),
    ]

    indicator = models.OneToOneField(Indicator, on_delete=models.CASCADE, related_name='compliance')
    evidence_status = models.CharField(max_length=50, choices=EVIDENCE_STATUS_CHOICES, default='missing')
    current_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    gap_summary = models.TextField(blank=True)
    next_action = models.TextField(blank=True)
    evidence_location = models.CharField(max_length=255, blank=True)
    ready_for_print_pack = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_score(self):
        # missing = 0
        # partial = 80% of max score where partial compliance is acceptable
        # ready = max score
        # verified = max score
        # not applicable = handled explicitly and documented
        max_score = float(self.indicator.max_score)
        if self.evidence_status == 'missing':
            return 0.0
        elif self.evidence_status == 'partial':
            return max_score * 0.8
        elif self.evidence_status in ['ready', 'verified']:
            return max_score
        elif self.evidence_status == 'not_applicable':
            return max_score # Excluded from total or scored as max so it doesn't penalize
        return 0.0

    def save(self, *args, **kwargs):
        self.current_score = self.calculate_score()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Compliance for {self.indicator.indicator_no}"
