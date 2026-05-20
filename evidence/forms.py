from django import forms
from .models import EvidenceItem
from indicators.models import Indicator

class EvidenceItemForm(forms.ModelForm):
    class Meta:
        model = EvidenceItem
        fields = ['title', 'evidence_type', 'file', 'external_url', 'evidence_date', 'description', 'linked_indicators']
        widgets = {
            'evidence_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'linked_indicators': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field in self.fields:
            if field != 'linked_indicators':
                self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['linked_indicators'].queryset = Indicator.objects.all().order_by('indicator_no')
