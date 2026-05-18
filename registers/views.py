from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import RegisterDefinition, RegisterEntry
from datetime import date

@login_required
def register_list(request):
    registers = RegisterDefinition.objects.filter(active=True).order_by('name')
    context = {'registers': registers}
    return render(request, 'registers/register_list.html', context)

@login_required
def register_detail(request, pk):
    register = get_object_or_404(RegisterDefinition, pk=pk)
    entries = register.entries.all().order_by('-entry_date')
    context = {
        'register': register,
        'entries': entries,
    }
    return render(request, 'registers/register_detail.html', context)

@login_required
def register_add_entry(request, pk):
    register = get_object_or_404(RegisterDefinition, pk=pk)
    
    if request.method == 'POST':
        # Simple JSON field extraction
        values = {}
        for key, val in request.POST.items():
            if key.startswith('field_'):
                values[key[6:]] = val
                
        entry_date_str = request.POST.get('entry_date') or str(date.today())
        remarks = request.POST.get('remarks', '')
        
        RegisterEntry.objects.create(
            register_definition=register,
            entry_date=entry_date_str,
            values_json=values,
            remarks=remarks,
            entered_by=request.user
        )
        return redirect('registers:detail', pk=register.pk)
        
    context = {
        'register': register,
        'today': str(date.today()),
    }
    return render(request, 'registers/register_add_entry.html', context)
