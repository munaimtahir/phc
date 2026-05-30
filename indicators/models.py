from django.db import models
from core.constants import FulfillmentStatus

class Indicator(models.Model):
    indicator_no = models.CharField(max_length=50, unique=True)
    functional_area_code = models.CharField(max_length=50)
    functional_area_name = models.CharField(max_length=255)
    standard_no = models.CharField(max_length=50)
    standard_code = models.CharField(max_length=50)
    standard_title = models.CharField(max_length=500)
    indicator_text = models.TextField()
    compliance_requirement = models.TextField(blank=True, null=True)
    surveyor_check = models.TextField(blank=True, null=True)
    scoring_note = models.TextField(blank=True, null=True)
    
    max_score = models.IntegerField(default=10)
    weightage_percent = models.IntegerField(default=100)
    partial_allowed = models.BooleanField(default=False)
    partial_score_percent = models.IntegerField(default=80)
    source_reference = models.CharField(max_length=255, blank=True, null=True)
    is_locked = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.indicator_no} - {self.indicator_text[:50]}"

    @property
    def calculated_status(self):
        reqs = self.evidence_requirements.all()
        if not reqs.exists():
            return FulfillmentStatus.MISSING
        
        statuses = [req.status for req in reqs]
        
        if all(s == FulfillmentStatus.VERIFIED for s in statuses):
            return FulfillmentStatus.VERIFIED
        
        # If all are either verified or ready, the indicator is ready
        if all(s in [FulfillmentStatus.VERIFIED, FulfillmentStatus.READY] for s in statuses):
            return FulfillmentStatus.READY
            
        # If there's any progress at all (at least one is not missing)
        if any(s != FulfillmentStatus.MISSING for s in statuses):
            return FulfillmentStatus.PARTIAL
            
        return FulfillmentStatus.MISSING

    @property
    def score(self):
        status = self.calculated_status
        if status == FulfillmentStatus.VERIFIED or status == FulfillmentStatus.READY:
            return self.max_score
        if status == FulfillmentStatus.PARTIAL and self.partial_allowed:
            return (self.partial_score_percent / 100) * self.max_score
        return 0
