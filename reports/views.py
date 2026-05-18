from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from indicators.models import Indicator

@login_required
def report_index(request):
    return render(request, 'reports/index.html')

@login_required
def score_summary(request):
    indicators = Indicator.objects.select_related('compliance').all()
    max_score = sum(i.max_score for i in indicators)
    current_score = sum(i.compliance.current_score for i in indicators)
    
    context = {
        'max_score': max_score,
        'current_score': round(current_score, 2),
        'readiness_percentage': round((current_score / max_score * 100) if max_score > 0 else 0, 1),
        'indicators': indicators,
    }
    return render(request, 'reports/score_summary.html', context)

@login_required
def missing_evidence(request):
    indicators = Indicator.objects.select_related('compliance').filter(
        compliance__evidence_status__in=['missing', 'partial']
    ).order_by('indicator_no')
    
    context = {
        'indicators': indicators,
    }
    return render(request, 'reports/missing_evidence.html', context)

@login_required
def surveyor_pack(request):
    indicators = Indicator.objects.select_related('compliance').filter(
        compliance__ready_for_print_pack=True
    ).order_by('standard_code', 'indicator_no')
    
    context = {
        'indicators': indicators,
    }
    return render(request, 'reports/surveyor_pack.html', context)
