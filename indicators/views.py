from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Indicator

@login_required
def indicator_list(request):
    indicators = Indicator.objects.select_related('compliance').all().order_by('indicator_no')
    
    # Filtering
    q = request.GET.get('q', '')
    if q:
        indicators = indicators.filter(
            Q(indicator_no__icontains=q) | 
            Q(indicator_text__icontains=q) | 
            Q(standard_title__icontains=q)
        )
        
    area = request.GET.get('area', '')
    if area:
        indicators = indicators.filter(functional_area_code=area)
        
    status = request.GET.get('status', '')
    if status:
        indicators = indicators.filter(compliance__evidence_status=status)

    areas = Indicator.objects.values_list('functional_area_code', 'functional_area_name').distinct()
    
    context = {
        'indicators': indicators,
        'areas': areas,
        'q': q,
        'selected_area': area,
        'selected_status': status,
    }
    return render(request, 'indicators/indicator_list.html', context)

@login_required
def indicator_detail(request, pk):
    indicator = get_object_or_404(Indicator.objects.select_related('compliance'), pk=pk)
    
    if request.method == 'POST':
        compliance = indicator.compliance
        compliance.evidence_status = request.POST.get('evidence_status', compliance.evidence_status)
        compliance.gap_summary = request.POST.get('gap_summary', compliance.gap_summary)
        compliance.next_action = request.POST.get('next_action', compliance.next_action)
        compliance.ready_for_print_pack = request.POST.get('ready_for_print_pack') == 'on'
        compliance.updated_by = request.user
        compliance.save()
        return redirect('indicators:detail', pk=indicator.pk)
        
    context = {
        'indicator': indicator,
    }
    return render(request, 'indicators/indicator_detail.html', context)
