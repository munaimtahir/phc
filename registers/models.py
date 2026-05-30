from django.db import models
from django.contrib.auth.models import User
from core.constants import RecurrenceMode

class RegisterDefinition(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True, null=True)
    linked_evidence_requirements = models.ManyToManyField('evidence.EvidenceRequirement', blank=True, related_name='linked_registers')
    frequency = models.CharField(max_length=100, blank=True, null=True)
    recurrence_mode = models.CharField(max_length=50, choices=RecurrenceMode.choices, default=RecurrenceMode.NONE)
    fields_schema = models.JSONField(default=dict)
    printable = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class RegisterEntry(models.Model):
    register_definition = models.ForeignKey(RegisterDefinition, on_delete=models.CASCADE, related_name='entries')
    entry_date = models.DateTimeField()
    values_json = models.JSONField(default=dict)
    entered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='entered_registers')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_registers')
    verified_at = models.DateTimeField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.register_definition.name} - {self.entry_date}"
