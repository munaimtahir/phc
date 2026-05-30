from django import forms
from .models import RegisterEntry

class RegisterEntryForm(forms.ModelForm):
    # Dynamic JSON schema fields can be added in the view
    
    class Meta:
        model = RegisterEntry
        fields = ['entry_date', 'remarks']
        widgets = {
            'entry_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }
