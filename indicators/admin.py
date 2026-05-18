from django.contrib import admin
from .models import Indicator, IndicatorCompliance

@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ('indicator_no', 'functional_area_code', 'standard_no', 'is_locked')
    search_fields = ('indicator_no', 'indicator_text', 'standard_title')
    list_filter = ('functional_area_code', 'is_locked', 'register_required', 'recurring_required')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_locked:
            return self.readonly_fields + ('indicator_no', 'functional_area_code', 'functional_area_name', 'standard_no', 'standard_code', 'standard_title', 'indicator_text', 'max_score', 'weightage_percent', 'compliance_requirement', 'surveyor_check', 'required_evidence', 'evidence_category', 'register_required', 'register_name', 'recurring_required', 'recurrence_frequency', 'document_to_generate', 'physical_action_required', 'source_reference')
        return self.readonly_fields

@admin.register(IndicatorCompliance)
class IndicatorComplianceAdmin(admin.ModelAdmin):
    list_display = ('indicator', 'evidence_status', 'current_score', 'ready_for_print_pack', 'updated_at')
    search_fields = ('indicator__indicator_no', 'indicator__indicator_text')
    list_filter = ('evidence_status', 'ready_for_print_pack')
    readonly_fields = ('current_score', 'updated_at')
