from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import EvidenceItem
from .forms import EvidenceItemForm
from indicators.models import Indicator

@login_required
def evidence_list(request):
    evidences = EvidenceItem.objects.prefetch_related('linked_indicators').all().order_by('-created_at')
    
    # Simple filtering
    q = request.GET.get('q', '')
    if q:
        evidences = evidences.filter(title__icontains=q)
        
    link_to = request.GET.get('link_to')
    
    context = {
        'evidences': evidences,
        'q': q,
        'link_to': link_to,
    }
    return render(request, 'evidence/evidence_list.html', context)

@login_required
def evidence_detail(request, pk):
    evidence = get_object_or_404(EvidenceItem.objects.prefetch_related('linked_indicators'), pk=pk)
    context = {
        'evidence': evidence,
    }
    return render(request, 'evidence/evidence_detail.html', context)

@login_required
def evidence_create(request):
    indicator_id = request.GET.get('indicator')
    initial_data = {}
    if indicator_id:
        indicator = get_object_or_404(Indicator, pk=indicator_id)
        initial_data['linked_indicators'] = [indicator]

    if request.method == 'POST':
        form = EvidenceItemForm(request.POST, request.FILES)
        if form.is_valid():
            evidence = form.save(commit=False)
            evidence.uploaded_by = request.user
            evidence.save()
            form.save_m2m() # Important for ManyToMany
            
            if indicator_id:
                return redirect('indicators:detail', pk=indicator_id)
            return redirect('evidence:list')
    else:
        form = EvidenceItemForm(initial=initial_data)
        
    context = {
        'form': form,
        'indicator_id': indicator_id,
    }
    return render(request, 'evidence/evidence_form.html', context)

@login_required
def evidence_link(request, pk):
    indicator_id = request.GET.get('indicator')
    if not indicator_id:
        return redirect('evidence:list')
        
    evidence = get_object_or_404(EvidenceItem, pk=pk)
    indicator = get_object_or_404(Indicator, pk=indicator_id)
    
    evidence.linked_indicators.add(indicator)
    return redirect('indicators:detail', pk=indicator_id)
