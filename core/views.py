from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from indicators.models import Indicator
from evidence.models import DocumentBatch, PlannedEvidenceDocument, GeneratedEvidenceDocument
from core.constants import FulfillmentStatus, GenerationStatus, DOCXStatus

def health_check(request):
    return JsonResponse({'status': 'ok'})

@login_required
def dashboard(request):
    indicators = Indicator.objects.all().select_related('evidence_profile').prefetch_related('evidence_requirements', 'evidence_requirements__fulfillments')
    
    total_indicators = indicators.count()
    
    # Status counts
    status_counts = {
        FulfillmentStatus.MISSING: 0,
        FulfillmentStatus.PARTIAL: 0,
        FulfillmentStatus.READY: 0,
        FulfillmentStatus.VERIFIED: 0,
    }
    # Gap counts
    gap_counts = {
        'upload_pending': 0,
        'register_pending': 0,
        'display_pending': 0,
        'physical_proof_pending': 0,
        'staff_awareness_pending': 0,
    }
    
    current_score = 0
    max_score = 0
    
    for ind in indicators:
        status = ind.calculated_status
        status_counts[status] += 1
            
        current_score += ind.score
        max_score += ind.max_score
        
        # Aggregate gaps for non-verified indicators
        if status != FulfillmentStatus.VERIFIED and ind.evidence_profile:
            profile = ind.evidence_profile
            if profile.upload_required:
                gap_counts['upload_pending'] += 1
            if profile.register_required:
                gap_counts['register_pending'] += 1
            if profile.display_required:
                gap_counts['display_pending'] += 1
            if profile.physical_proof_required:
                gap_counts['physical_proof_pending'] += 1
            if profile.staff_awareness_required:
                gap_counts['staff_awareness_pending'] += 1
        
    readiness_percent = (current_score / max_score * 100) if max_score > 0 else 0
    
    # Batch Stats
    total_batches = DocumentBatch.objects.count()
    total_planned_docs = PlannedEvidenceDocument.objects.count()
    drafted_docs = PlannedEvidenceDocument.objects.filter(generation_status=GenerationStatus.DRAFTED).count()
    
    total_generated_docs = GeneratedEvidenceDocument.objects.count()
    docx_available_count = GeneratedEvidenceDocument.objects.filter(docx_status=DOCXStatus.GENERATED_WAITING_APPROVAL).count()
    docx_missing_count = total_generated_docs - docx_available_count

    context = {
        'total_indicators': total_indicators,
        'missing_indicators': status_counts[FulfillmentStatus.MISSING],
        'partial_indicators': status_counts[FulfillmentStatus.PARTIAL],
        'ready_indicators': status_counts[FulfillmentStatus.READY],
        'verified_indicators': status_counts[FulfillmentStatus.VERIFIED],
        'current_score': round(current_score, 2),
        'max_score': max_score,
        'readiness_percent': round(readiness_percent, 2),
        'gap_counts': gap_counts,
        'total_batches': total_batches,
        'total_planned_docs': total_planned_docs,
        'drafted_docs': drafted_docs,
        'total_generated_docs': total_generated_docs,
        'docx_available_count': docx_available_count,
        'docx_missing_count': docx_missing_count,
    }
    return render(request, 'core/dashboard.html', context)
