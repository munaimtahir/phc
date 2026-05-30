from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Indicator
from evidence.models import EvidenceRequirement
from .services import generate_ai_prompt

@login_required
def indicator_list(request):
    indicators = Indicator.objects.all().order_by('indicator_no')
    
    # basic filtering
    func_area = request.GET.get('functional_area')
    if func_area:
        indicators = indicators.filter(functional_area_code=func_area)
        
    context = {
        'indicators': indicators,
    }
    return render(request, 'indicators/list.html', context)

@login_required
def indicator_detail(request, pk):
    indicator = get_object_or_404(Indicator, pk=pk)
    
    context = {
        'indicator': indicator,
        'requirements': indicator.evidence_requirements.all()
    }
    return render(request, 'indicators/detail.html', context)

@login_required
def generate_prompt_view(request, pk, req_pk):
    indicator = get_object_or_404(Indicator, pk=pk)
    requirement = get_object_or_404(EvidenceRequirement, pk=req_pk, indicator=indicator)
    
    prompt_type = request.GET.get('type', 'SOP / Policy')
    
    prompt_text = generate_ai_prompt(indicator, requirement, prompt_type)
    
    if request.GET.get('download'):
        response = HttpResponse(prompt_text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="prompt_{indicator.indicator_no}_{requirement.pk}.txt"'
        return response
        
    context = {
        'indicator': indicator,
        'requirement': requirement,
        'prompt_text': prompt_text,
        'prompt_type': prompt_type
    }
    return render(request, 'indicators/prompt.html', context)
