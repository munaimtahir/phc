from django import forms
from .models import EvidenceItem, EvidenceRequirementFulfillment
from core.constants import EvidenceType, DocumentType, ApprovalStatus

class EvidenceItemForm(forms.ModelForm):
    class Meta:
        model = EvidenceItem
        fields = [
            'title', 'evidence_type', 'document_type', 'file', 
            'external_url', 'physical_file_location', 'display_location',
            'evidence_date', 'version', 'document_code', 'effective_date',
            'review_date', 'approval_status', 'description'
        ]
        widgets = {
            'evidence_date': forms.DateInput(attrs={'type': 'date'}),
            'effective_date': forms.DateInput(attrs={'type': 'date'}),
            'review_date': forms.DateInput(attrs={'type': 'date'}),
        }

class EvidenceLinkageForm(forms.ModelForm):
    class Meta:
        model = EvidenceRequirementFulfillment
        fields = ['evidence_requirement', 'status', 'remarks']

class SignedDocumentUploadForm(forms.Form):
    title = forms.CharField(max_length=255)
    evidence_type = forms.ChoiceField(choices=EvidenceType.choices, initial=EvidenceType.CONTROLLED_DOCUMENT)
    document_type = forms.ChoiceField(choices=DocumentType.choices, initial=DocumentType.SOP)
    file = forms.FileField()
    approval_status = forms.ChoiceField(choices=ApprovalStatus.choices, initial=ApprovalStatus.PENDING_REVIEW)
    remarks = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))

    display_confirmed = forms.BooleanField(required=False, help_text='Confirm display requirement is satisfied (if applicable).')
    physical_confirmed = forms.BooleanField(required=False, help_text='Confirm physical proof requirement is satisfied (if applicable).')
    staff_awareness_confirmed = forms.BooleanField(required=False, help_text='Confirm staff awareness requirement is satisfied (if applicable).')
    register_confirmed = forms.BooleanField(required=False, help_text='Confirm register/logbook requirement is satisfied (if applicable).')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ['title', 'evidence_type', 'document_type', 'approval_status', 'file', 'remarks']:
            field = self.fields.get(name)
            if not field:
                continue
            css = 'form-control'
            if getattr(field.widget, 'input_type', '') == 'file':
                css = 'form-control'
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs.setdefault('class', css)
        for name in ['display_confirmed', 'physical_confirmed', 'staff_awareness_confirmed', 'register_confirmed']:
            field = self.fields.get(name)
            if field and hasattr(field.widget, 'attrs'):
                field.widget.attrs.setdefault('class', 'form-check-input')
