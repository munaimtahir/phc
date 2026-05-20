from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Indicator
from .services.prompt_generator import (
    PROMPT_TYPES,
    PROMPT_TYPE_SOP_POLICY,
    build_prompt,
)

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
    selected_prompt_type = request.GET.get('prompt_type', PROMPT_TYPE_SOP_POLICY)
    allowed_prompt_types = {prompt_key for prompt_key, _ in PROMPT_TYPES}
    if selected_prompt_type not in allowed_prompt_types:
        selected_prompt_type = PROMPT_TYPE_SOP_POLICY
    
    if request.method == 'POST':
        compliance = indicator.compliance
        compliance.evidence_status = request.POST.get('evidence_status', compliance.evidence_status)
        compliance.gap_summary = request.POST.get('gap_summary', compliance.gap_summary)
        compliance.next_action = request.POST.get('next_action', compliance.next_action)
        compliance.ready_for_print_pack = request.POST.get('ready_for_print_pack') == 'on'
        compliance.updated_by = request.user
        compliance.save()
        detail_url = reverse('indicators:detail', kwargs={'pk': indicator.pk})
        return redirect(f"{detail_url}?prompt_type={selected_prompt_type}")

    generated_prompt = build_prompt(indicator, selected_prompt_type)
    if request.GET.get('download') == '1':
        prompt_label = dict(PROMPT_TYPES).get(selected_prompt_type, 'prompt').lower().replace(' / ', '_').replace(' ', '_')
        response = HttpResponse(generated_prompt, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = (
            f'attachment; filename="indicator_{indicator.indicator_no}_{prompt_label}.txt"'
        )
        return response
        
    context = {
        'indicator': indicator,
        'prompt_types': PROMPT_TYPES,
        'selected_prompt_type': selected_prompt_type,
        'generated_prompt': generated_prompt,
    }
    return render(request, 'indicators/indicator_detail.html', context)
