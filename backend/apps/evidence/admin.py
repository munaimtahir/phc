from django.contrib import admin

from .models import EvidenceRecord


@admin.register(EvidenceRecord)
class EvidenceRecordAdmin(admin.ModelAdmin):
    list_display = ["id", "indicator", "period_label", "status", "is_current", "submitted_at"]
    list_filter = ["status", "is_current"]
