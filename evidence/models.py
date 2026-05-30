from django.db import models
from django.contrib.auth.models import User
from indicators.models import Indicator
from core.constants import (
    EvidenceType, DocumentType, AIGenerationMode, RecurrenceMode,
    ApprovalStatus, SourceType, FulfillmentStatus,
    PrimaryEvidenceType, RecurrenceFrequency, ProfileConfidence, ProfileSource,
    Priority, BatchType, DocumentKind, GenerationStatus, EvidenceNature,
    GeneratedDocumentStatus, DOCXStatus
)

class GeneratedEvidenceDocument(models.Model):
    planned_document = models.ForeignKey('evidence.PlannedEvidenceDocument', on_delete=models.CASCADE, related_name='generated_drafts')
    batch = models.ForeignKey('evidence.DocumentBatch', on_delete=models.CASCADE, related_name='generated_documents')
    title = models.CharField(max_length=255)
    document_code = models.CharField(max_length=50)
    version = models.CharField(max_length=20, default='1.0')
    status = models.CharField(max_length=50, choices=GeneratedDocumentStatus.choices, default=GeneratedDocumentStatus.DRAFT)
    content_markdown = models.TextField()
    output_file = models.FileField(upload_to='generated_drafts/', blank=True, null=True)

    docx_file = models.FileField(upload_to='generated_documents_docx/', blank=True, null=True)
    docx_generated_at = models.DateTimeField(blank=True, null=True)
    docx_status = models.CharField(max_length=50, choices=DOCXStatus.choices, default=DOCXStatus.NOT_GENERATED)
    docx_version = models.CharField(max_length=20, default='1.0')
    
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_documents')
    reviewed_at = models.DateTimeField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    
    is_print_ready = models.BooleanField(default=False)
    linked_evidence_item = models.OneToOneField('evidence.EvidenceItem', on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_source')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.document_code} - {self.title} ({self.status})"

class DocumentBatch(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    functional_area = models.CharField(max_length=50, blank=True, null=True)
    sequence_order = models.IntegerField(default=0)
    priority = models.CharField(max_length=50, choices=Priority.choices, default=Priority.MEDIUM)
    batch_type = models.CharField(max_length=50, choices=BatchType.choices, default=BatchType.MIXED)
    
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def document_stats(self):
        docs = self.planned_documents.all()
        total = docs.count()
        ready = sum(1 for d in docs if d.calculated_status in [FulfillmentStatus.READY, FulfillmentStatus.VERIFIED])
        partial = sum(1 for d in docs if d.calculated_status == FulfillmentStatus.PARTIAL)
        missing = total - ready - partial
        return {
            'total': total,
            'ready': ready,
            'partial': partial,
            'missing': missing,
            'percent': (ready / total * 100) if total > 0 else 0
        }

    @property
    def indicator_stats(self):
        # Unique indicators linked via documents in this batch
        from indicators.models import Indicator
        indicators = Indicator.objects.filter(planned_documents__batch=self).distinct()
        total = indicators.count()
        ready = sum(1 for i in indicators if i.calculated_status in [FulfillmentStatus.READY, FulfillmentStatus.VERIFIED])
        partial = sum(1 for i in indicators if i.calculated_status == FulfillmentStatus.PARTIAL)
        missing = total - ready - partial
        return {
            'total': total,
            'ready': ready,
            'partial': partial,
            'missing': missing
        }

    class Meta:
        verbose_name_plural = "Document Batches"

class PlannedEvidenceDocument(models.Model):
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    batch = models.ForeignKey(DocumentBatch, on_delete=models.CASCADE, related_name='planned_documents')
    document_kind = models.CharField(max_length=50, choices=DocumentKind.choices, default=DocumentKind.OTHER)
    generation_status = models.CharField(max_length=50, choices=GenerationStatus.choices, default=GenerationStatus.PLANNED)
    evidence_nature = models.CharField(max_length=50, choices=EvidenceNature.choices, default=EvidenceNature.ONE_TIME)
    frequency = models.CharField(max_length=50, choices=RecurrenceFrequency.choices, default=RecurrenceFrequency.NONE)
    
    description = models.TextField(blank=True, null=True)
    practical_instructions = models.TextField(blank=True, null=True)
    suggested_file_name = models.CharField(max_length=255, blank=True, null=True)
    physical_file_section = models.CharField(max_length=255, blank=True, null=True)
    display_location = models.CharField(max_length=255, blank=True, null=True)
    
    staff_awareness_needed = models.BooleanField(default=False)
    physical_confirmation_needed = models.BooleanField(default=False)
    display_confirmation_needed = models.BooleanField(default=False)
    upload_needed = models.BooleanField(default=True)
    register_entry_needed = models.BooleanField(default=False)
    
    linked_register = models.ForeignKey('registers.RegisterDefinition', on_delete=models.SET_NULL, null=True, blank=True)
    is_combined_document = models.BooleanField(default=False)
    can_satisfy_multiple_indicators = models.BooleanField(default=False)
    
    priority = models.CharField(max_length=50, choices=Priority.choices, default=Priority.MEDIUM)
    sort_order = models.IntegerField(default=0)
    
    indicators = models.ManyToManyField('indicators.Indicator', blank=True, related_name='planned_documents')
    evidence_requirements = models.ManyToManyField('evidence.EvidenceRequirement', blank=True, related_name='planned_documents')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.title}"

    @property
    def calculated_status(self):
        # Derived from linked indicators
        indicators = self.indicators.all()
        if not indicators.exists():
            return FulfillmentStatus.MISSING
        
        statuses = [ind.calculated_status for ind in indicators]
        
        if all(s == FulfillmentStatus.VERIFIED for s in statuses):
            return FulfillmentStatus.VERIFIED
        
        if all(s in [FulfillmentStatus.VERIFIED, FulfillmentStatus.READY] for s in statuses):
            return FulfillmentStatus.READY
            
        if any(s in [FulfillmentStatus.VERIFIED, FulfillmentStatus.READY, FulfillmentStatus.PARTIAL] for s in statuses):
            return FulfillmentStatus.PARTIAL
            
        return FulfillmentStatus.MISSING

class EvidenceRequirement(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name='evidence_requirements')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    evidence_type = models.CharField(max_length=50, choices=EvidenceType.choices, default=EvidenceType.OTHER)
    document_type = models.CharField(max_length=50, choices=DocumentType.choices, default=DocumentType.OTHER)
    ai_generation_mode = models.CharField(max_length=50, choices=AIGenerationMode.choices, default=AIGenerationMode.NO_AI_NEEDED)
    recurrence_mode = models.CharField(max_length=50, choices=RecurrenceMode.choices, default=RecurrenceMode.NONE)
    recurrence_frequency = models.CharField(max_length=100, blank=True, null=True)
    minimum_required_count = models.IntegerField(default=1)
    
    display_required = models.BooleanField(default=False)
    physical_verification_required = models.BooleanField(default=False)
    human_approval_required = models.BooleanField(default=False)
    upload_required = models.BooleanField(default=False)
    template_reusable = models.BooleanField(default=False)
    evidence_reuse_policy = models.CharField(max_length=100, blank=True, null=True)
    
    sort_order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.indicator.indicator_no} - {self.title}"

    @property
    def status(self):
        profile = getattr(self.indicator, 'evidence_profile', None)
        if not profile:
            return FulfillmentStatus.MISSING # Cannot determine status without a profile

        fulfillments = self.fulfillments.all()
        if not fulfillments.exists():
            return FulfillmentStatus.MISSING

        # Check if any fulfillment meets all profile conditions
        for f in fulfillments:
            is_ready = True
            if profile.upload_required and not f.evidence_item:
                is_ready = False
            if profile.register_required and not getattr(f, 'register_confirmed', False):
                is_ready = False
            if profile.physical_proof_required and not f.physical_confirmed:
                is_ready = False
            if profile.display_required and not f.display_confirmed:
                is_ready = False
            if profile.staff_awareness_required and not f.staff_awareness_confirmed:
                is_ready = False
            
            if is_ready:
                # If a user has fully verified this fulfillment, it's VERIFIED
                if f.status == FulfillmentStatus.VERIFIED:
                    return FulfillmentStatus.VERIFIED
                # Otherwise, it's at least READY
                return FulfillmentStatus.READY

        # If no single fulfillment is fully ready, the requirement is PARTIAL
        return FulfillmentStatus.PARTIAL

class EvidenceItem(models.Model):
    title = models.CharField(max_length=255)
    evidence_type = models.CharField(max_length=50, choices=EvidenceType.choices, default=EvidenceType.OTHER)
    document_type = models.CharField(max_length=50, choices=DocumentType.choices, default=DocumentType.OTHER)
    
    file = models.FileField(upload_to='evidence_files/', blank=True, null=True)
    external_url = models.URLField(max_length=500, blank=True, null=True)
    physical_file_location = models.CharField(max_length=255, blank=True, null=True)
    display_location = models.CharField(max_length=255, blank=True, null=True)
    
    evidence_date = models.DateField(blank=True, null=True)
    version = models.CharField(max_length=50, blank=True, null=True)
    document_code = models.CharField(max_length=100, blank=True, null=True)
    effective_date = models.DateField(blank=True, null=True)
    review_date = models.DateField(blank=True, null=True)
    
    approval_status = models.CharField(max_length=50, choices=ApprovalStatus.choices, default=ApprovalStatus.DRAFT)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_evidence')
    approved_at = models.DateTimeField(blank=True, null=True)
    
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_evidence')
    planned_document = models.ForeignKey('evidence.PlannedEvidenceDocument', on_delete=models.SET_NULL, null=True, blank=True, related_name='evidence_items')
    
    source_type = models.CharField(max_length=50, choices=SourceType.choices, default=SourceType.UPLOADED_FILE)
    source_register_entry = models.ForeignKey('registers.RegisterEntry', on_delete=models.SET_NULL, null=True, blank=True, related_name='linked_evidence_items')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class EvidenceRequirementFulfillment(models.Model):
    evidence_requirement = models.ForeignKey(EvidenceRequirement, on_delete=models.CASCADE, related_name='fulfillments')
    evidence_item = models.ForeignKey(EvidenceItem, on_delete=models.CASCADE, related_name='requirement_fulfillments')
    status = models.CharField(max_length=50, choices=FulfillmentStatus.choices, default=FulfillmentStatus.DRAFT)
    
    physical_confirmed = models.BooleanField(default=False)
    display_confirmed = models.BooleanField(default=False)
    staff_awareness_confirmed = models.BooleanField(default=False)
    register_confirmed = models.BooleanField(default=False)
    
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.evidence_requirement} - {self.status}"


class IndicatorEvidenceProfile(models.Model):
    indicator = models.OneToOneField('indicators.Indicator', on_delete=models.CASCADE, related_name='evidence_profile')
    
    primary_evidence_type = models.CharField(max_length=50, choices=PrimaryEvidenceType.choices, default=PrimaryEvidenceType.OTHER)
    
    upload_required = models.BooleanField(default=False)
    register_required = models.BooleanField(default=False)
    physical_proof_required = models.BooleanField(default=False)
    display_required = models.BooleanField(default=False)
    staff_awareness_required = models.BooleanField(default=False)
    approval_required = models.BooleanField(default=False)
    recurring_required = models.BooleanField(default=False)
    
    recurrence_frequency = models.CharField(max_length=50, choices=RecurrenceFrequency.choices, default=RecurrenceFrequency.NONE)
    suggested_register = models.ForeignKey('registers.RegisterDefinition', on_delete=models.SET_NULL, null=True, blank=True)
    display_location = models.CharField(max_length=255, blank=True, null=True)
    
    physical_verification_note = models.TextField(blank=True, null=True)
    staff_awareness_note = models.TextField(blank=True, null=True)
    
    readiness_rule = models.TextField(blank=True, null=True)
    partial_rule = models.TextField(blank=True, null=True)
    missing_rule = models.TextField(blank=True, null=True)
    user_action_prompt = models.TextField(blank=True, null=True)
    
    ai_mapping_notes = models.TextField(blank=True, null=True)
    profile_confidence = models.CharField(max_length=50, choices=ProfileConfidence.choices, default=ProfileConfidence.LOW)
    profile_source = models.CharField(max_length=50, choices=ProfileSource.choices, default=ProfileSource.MANUAL_REVIEWED)

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.indicator.indicator_no}"
