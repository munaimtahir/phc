from django.db import models
from django.conf import settings
from indicators.models import Indicator

class EvidenceItem(models.Model):
    EVIDENCE_TYPES = [
        ('SOP / Policy', 'SOP / Policy'),
        ('Register / Logbook', 'Register / Logbook'),
        ('Recurring Record', 'Recurring Record'),
        ('Physical Display / Photo', 'Physical Display / Photo'),
        ('Certificate / License / MOU', 'Certificate / License / MOU'),
        ('Staff File / HR Record', 'Staff File / HR Record'),
        ('Patient Record / Reporting System', 'Patient Record / Reporting System'),
        ('Audit / QA Report', 'Audit / QA Report'),
        ('Other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    evidence_type = models.CharField(max_length=100, choices=EVIDENCE_TYPES, default='Other')
    file = models.FileField(upload_to='evidence_files/', null=True, blank=True)
    external_url = models.URLField(max_length=500, null=True, blank=True)
    evidence_date = models.DateField(null=True, blank=True)
    linked_indicators = models.ManyToManyField(Indicator, related_name='evidence_items', blank=True)
    description = models.TextField(blank=True)
    
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
