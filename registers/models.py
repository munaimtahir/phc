from django.db import models
from django.conf import settings
from indicators.models import Indicator

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

class RegisterDefinition(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True)
    linked_indicators = models.ManyToManyField(Indicator, related_name='registers', blank=True)
    frequency = models.CharField(max_length=50, blank=True, help_text="e.g. Daily, Weekly, Monthly, Quarterly, Annual, Event-based")
    fields_schema = models.JSONField(default=dict, blank=True, help_text="JSON schema for register fields")
    printable = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def last_entry_date(self):
        last_entry = self.entries.order_by('-entry_date').first()
        return last_entry.entry_date if last_entry else None

    @property
    def next_due_date(self):
        last_date = self.last_entry_date
        if not last_date or self.frequency in ['Event-based', 'One-time', '', None]:
            return None
            
        freq = self.frequency.lower()
        if freq == 'daily':
            return last_date + timedelta(days=1)
        elif freq == 'weekly':
            return last_date + timedelta(weeks=1)
        elif freq == 'monthly':
            return last_date + relativedelta(months=1)
        elif freq == 'quarterly':
            return last_date + relativedelta(months=3)
        elif freq == 'annual' or freq == 'yearly':
            return last_date + relativedelta(years=1)
        return None

    @property
    def is_overdue(self):
        due_date = self.next_due_date
        if not due_date:
            return False
        return date.today() > due_date

    @property
    def is_due_soon(self):
        due_date = self.next_due_date
        if not due_date:
            return False
        # default due soon window: 7 days
        today = date.today()
        return today <= due_date <= today + timedelta(days=7)


class RegisterEntry(models.Model):
    register_definition = models.ForeignKey(RegisterDefinition, on_delete=models.CASCADE, related_name='entries')
    entry_date = models.DateField()
    values_json = models.JSONField(default=dict, blank=True)
    
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='entered_registers')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_registers')
    verified_at = models.DateTimeField(null=True, blank=True)
    
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.register_definition.name} - {self.entry_date}"
