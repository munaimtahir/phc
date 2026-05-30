from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from indicators.models import Indicator
from evidence.models import EvidenceRequirement, EvidenceItem
from registers.models import RegisterDefinition
from core.constants import FulfillmentStatus

@login_required
def reports_home(request):
    return render(request, 'reports/home.html')

@login_required
def score_summary(request):
    indicators = Indicator.objects.all().prefetch_related('evidence_requirements', 'evidence_requirements__fulfillments')
    
    current_score = sum(ind.score for ind in indicators)
    max_score = sum(ind.max_score for ind in indicators)
    readiness_percent = (current_score / max_score * 100) if max_score > 0 else 0
    
    context = {
        'current_score': round(current_score, 2),
        'max_score': max_score,
        'readiness_percent': round(readiness_percent, 2),
        'indicators': indicators
    }
    return render(request, 'reports/score_summary.html', context)

@login_required
def missing_evidence(request):
    requirements = EvidenceRequirement.objects.all().select_related('indicator').prefetch_related('fulfillments')
    
    missing_requirements = [req for req in requirements if req.status == FulfillmentStatus.MISSING]
    
    context = {
        'missing_requirements': missing_requirements
    }
    return render(request, 'reports/missing_evidence.html', context)

@login_required
def evidence_index(request):
    items = EvidenceItem.objects.all().order_by('-evidence_date').prefetch_related('requirement_fulfillments__evidence_requirement__indicator')
    context = {'items': items}
    return render(request, 'reports/evidence_index.html', context)

@login_required
def recurring_compliance(request):
    registers = RegisterDefinition.objects.filter(
        recurrence_mode__in=['SCHEDULED_RECURRING', 'EVENT_DRIVEN'],
        active=True
    ).prefetch_related('entries')
    
    context = {'registers': registers}
    return render(request, 'reports/recurring.html', context)

@login_required
def surveyor_pack(request):
    indicators = Indicator.objects.all().order_by('functional_area_code', 'standard_no', 'indicator_no').prefetch_related('evidence_requirements', 'evidence_requirements__fulfillments__evidence_item')
    
    context = {'indicators': indicators}
    return render(request, 'reports/surveyor_pack.html', context)
