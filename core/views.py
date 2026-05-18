from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from indicators.models import Indicator, IndicatorCompliance
from evidence.models import EvidenceItem
from registers.models import RegisterDefinition

def health_check(request):
    return HttpResponse("OK")

@login_required
def dashboard(request):
    indicators = Indicator.objects.select_related('compliance').all()
    
    total_indicators = indicators.count()
    if total_indicators == 0:
        return render(request, 'core/dashboard.html', {'is_empty': True})
        
    stats = {
        'total': total_indicators,
        'missing': indicators.filter(compliance__evidence_status='missing').count(),
        'partial': indicators.filter(compliance__evidence_status='partial').count(),
        'ready': indicators.filter(compliance__evidence_status='ready').count(),
        'verified': indicators.filter(compliance__evidence_status='verified').count(),
    }
    
    max_score = sum(i.max_score for i in indicators)
    current_score = sum(i.compliance.current_score for i in indicators)
    readiness_percentage = (current_score / max_score * 100) if max_score > 0 else 0
    
    evidence_count = EvidenceItem.objects.count()
    
    registers = RegisterDefinition.objects.filter(active=True)
    active_registers = registers.count()
    
    # Check registers logic
    overdue_registers = []
    due_soon_registers = []
    for r in registers:
        if r.is_overdue:
            overdue_registers.append(r)
        elif r.is_due_soon:
            due_soon_registers.append(r)
            
    recent_updates = IndicatorCompliance.objects.select_related('indicator').order_by('-updated_at')[:5]
    
    # Area summary
    areas = Indicator.objects.values('functional_area_code').annotate(
        total=Count('id'),
    ).order_by('functional_area_code')
    
    context = {
        'stats': stats,
        'max_score': max_score,
        'current_score': round(current_score, 2),
        'readiness_percentage': round(readiness_percentage, 1),
        'evidence_count': evidence_count,
        'active_registers': active_registers,
        'overdue_registers': overdue_registers,
        'due_soon_registers': due_soon_registers,
        'recent_updates': recent_updates,
        'areas': areas,
    }
    
    return render(request, 'core/dashboard.html', context)
