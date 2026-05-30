from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import RegisterDefinition
from .forms import RegisterEntryForm
from evidence.models import EvidenceItem, SourceType, EvidenceRequirementFulfillment

@login_required
def register_list(request):
    registers = RegisterDefinition.objects.filter(active=True).order_by('name')
    context = {'registers': registers}
    return render(request, 'registers/list.html', context)

@login_required
def register_detail(request, pk):
    register = get_object_or_404(RegisterDefinition, pk=pk)
    entries = register.entries.all().order_by('-entry_date')
    
    context = {
        'register': register,
        'entries': entries
    }
    return render(request, 'registers/detail.html', context)

@login_required
def add_entry(request, pk):
    register = get_object_or_404(RegisterDefinition, pk=pk)
    
    if request.method == 'POST':
        form = RegisterEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.register_definition = register
            entry.entered_by = request.user
            
            # Simple handling of dynamic JSON values for MVP
            values = {}
            for key, value in request.POST.items():
                if key.startswith('json_'):
                    field_name = key.replace('json_', '')
                    values[field_name] = value
            entry.values_json = values
            entry.save()
            
            # Auto-link as evidence
            if register.linked_evidence_requirements.exists():
                evidence_item = EvidenceItem.objects.create(
                    title=f"{register.name} Entry: {entry.entry_date.strftime('%Y-%m-%d')}",
                    source_type=SourceType.REGISTER_ENTRY,
                    source_register_entry=entry,
                    uploaded_by=request.user,
                    evidence_date=entry.entry_date.date()
                )
                for req in register.linked_evidence_requirements.all():
                    EvidenceRequirementFulfillment.objects.create(
                        evidence_requirement=req,
                        evidence_item=evidence_item,
                        status='PENDING_REVIEW'
                    )
            
            messages.success(request, 'Register entry added successfully.')
            return redirect('register_detail', pk=register.pk)
    else:
        form = RegisterEntryForm(initial={'entry_date': timezone.now()})
        
    context = {
        'register': register,
        'form': form
    }
    return render(request, 'registers/add_entry.html', context)

@login_required
def register_print(request, pk):
    register = get_object_or_404(RegisterDefinition, pk=pk)
    entries = register.entries.all().order_by('-entry_date')[:50] # Limit for print
    
    context = {
        'register': register,
        'entries': entries
    }
    return render(request, 'registers/print.html', context)
