from django.contrib import admin
from .models import EvidenceRequirement, EvidenceItem, EvidenceRequirementFulfillment, IndicatorEvidenceProfile, DocumentBatch, PlannedEvidenceDocument, GeneratedEvidenceDocument

@admin.register(GeneratedEvidenceDocument)
class GeneratedEvidenceDocumentAdmin(admin.ModelAdmin):
    list_display = ('document_code', 'title', 'batch', 'status', 'version', 'is_print_ready', 'generated_at')
    list_filter = ('batch', 'status', 'is_print_ready', 'generated_at')
    search_fields = ('document_code', 'title', 'content_markdown', 'remarks')
    readonly_fields = ('generated_at', 'updated_at')

@admin.register(DocumentBatch)
class DocumentBatchAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'batch_type', 'priority', 'sequence_order', 'active')
    list_filter = ('batch_type', 'priority', 'active')
    search_fields = ('code', 'name', 'description')

@admin.register(PlannedEvidenceDocument)
class PlannedEvidenceDocumentAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'batch', 'document_kind', 'generation_status', 'priority')
    list_filter = ('batch', 'document_kind', 'generation_status', 'priority', 'evidence_nature')
    search_fields = ('code', 'title', 'description')
    filter_horizontal = ('indicators', 'evidence_requirements')

@admin.register(IndicatorEvidenceProfile)
class IndicatorEvidenceProfileAdmin(admin.ModelAdmin):
    list_display = ('indicator', 'primary_evidence_type', 'profile_confidence', 'profile_source', 'active')
    list_filter = ('primary_evidence_type', 'profile_confidence', 'profile_source', 'active', 'upload_required', 'register_required')
    search_fields = ('indicator__indicator_no', 'indicator__indicator_text', 'user_action_prompt')
    raw_id_fields = ('indicator', 'suggested_register')

@admin.register(EvidenceRequirement)
class EvidenceRequirementAdmin(admin.ModelAdmin):
    list_display = ('title', 'indicator', 'evidence_type', 'document_type', 'active')
    list_filter = ('evidence_type', 'document_type', 'active', 'ai_generation_mode')
    search_fields = ('title', 'indicator__indicator_no')

@admin.register(EvidenceItem)
class EvidenceItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'evidence_type', 'document_type', 'approval_status', 'evidence_date')
    list_filter = ('approval_status', 'evidence_type', 'document_type')
    search_fields = ('title', 'document_code')

@admin.register(EvidenceRequirementFulfillment)
class EvidenceRequirementFulfillmentAdmin(admin.ModelAdmin):
    list_display = ('evidence_requirement', 'evidence_item', 'status', 'verified_at')
    list_filter = ('status',)
