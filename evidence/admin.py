from django.contrib import admin
from .models import EvidenceItem

@admin.register(EvidenceItem)
class EvidenceItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'evidence_type', 'evidence_date', 'uploaded_by', 'created_at')
    list_filter = ('evidence_type', 'evidence_date')
    search_fields = ('title', 'description')
    filter_horizontal = ('linked_indicators',)
