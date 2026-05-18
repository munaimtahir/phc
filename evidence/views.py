from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import EvidenceItem

@login_required
def evidence_list(request):
    evidences = EvidenceItem.objects.prefetch_related('linked_indicators').all().order_by('-created_at')
    
    # Simple filtering
    q = request.GET.get('q', '')
    if q:
        evidences = evidences.filter(title__icontains=q)
        
    context = {
        'evidences': evidences,
        'q': q,
    }
    return render(request, 'evidence/evidence_list.html', context)

@login_required
def evidence_detail(request, pk):
    evidence = get_object_or_404(EvidenceItem.objects.prefetch_related('linked_indicators'), pk=pk)
    context = {
        'evidence': evidence,
    }
    return render(request, 'evidence/evidence_detail.html', context)
