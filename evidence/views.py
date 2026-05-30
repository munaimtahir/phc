from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import EvidenceItem, EvidenceRequirementFulfillment, EvidenceRequirement, DocumentBatch, PlannedEvidenceDocument, GeneratedEvidenceDocument
from indicators.models import Indicator
from core.constants import FulfillmentStatus, ApprovalStatus, DOCXStatus, GeneratedDocumentStatus
from .forms import EvidenceItemForm, EvidenceLinkageForm, SignedDocumentUploadForm
import markdown
import os
import csv
import io
import tempfile
import zipfile
from django.http import FileResponse, HttpResponse, HttpResponseBadRequest
from django.utils import timezone

@login_required
def batch_list(request):
    batches = DocumentBatch.objects.filter(active=True).order_by('sequence_order')
    context = {'batches': batches}
    return render(request, 'evidence/batch_list.html', context)

@login_required
def batch_detail(request, pk):
    batch = get_object_or_404(DocumentBatch, pk=pk)
    planned_docs = batch.planned_documents.all().order_by('sort_order', 'code')
    
    # Get all indicators linked to this batch via planned documents
    indicators = Indicator.objects.filter(planned_documents__batch=batch).distinct()
    
    context = {
        'batch': batch,
        'planned_documents': planned_docs,
        'indicators': indicators,
    }
    return render(request, 'evidence/batch_detail.html', context)

@login_required
def planned_doc_detail(request, pk):
    doc = get_object_or_404(PlannedEvidenceDocument, pk=pk)
    indicators = doc.indicators.all()
    requirements = doc.evidence_requirements.all()
    
    context = {
        'document': doc,
        'indicators': indicators,
        'requirements': requirements,
    }
    return render(request, 'evidence/planned_doc_detail.html', context)

@login_required
def generated_doc_detail(request, pk):
    doc = get_object_or_404(GeneratedEvidenceDocument, pk=pk)
    html_content = markdown.markdown(doc.content_markdown, extensions=['tables'])

    context = {
        'document': doc,
        'html_content': html_content,
    }
    return render(request, 'evidence/generated_doc_detail.html', context)

@login_required
def download_docx(request, pk):
    doc = get_object_or_404(GeneratedEvidenceDocument, pk=pk)
    if not doc.docx_file:
        from .services.docx_generator import generate_docx_for_generated_document
        generate_docx_for_generated_document(doc)
    response = FileResponse(doc.docx_file.open('rb'), as_attachment=True, filename=os.path.basename(doc.docx_file.name))
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    return response

def _build_zip_response(zip_filename, entries):
    buffer = tempfile.SpooledTemporaryFile(max_size=1024 * 1024 * 25)
    with zipfile.ZipFile(buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for arcname, file_field in entries:
            if not file_field:
                continue
            try:
                file_path = file_field.path
            except Exception:
                continue
            if not os.path.exists(file_path):
                continue
            zf.write(file_path, arcname=arcname)
    buffer.seek(0)
    response = FileResponse(buffer, as_attachment=True, filename=zip_filename)
    response['Content-Type'] = 'application/zip'
    return response

@login_required
def document_transfer_center(request):
    batches = DocumentBatch.objects.filter(active=True).order_by('sequence_order', 'code')

    selected_batch_id = request.GET.get('batch')
    docs_qs = GeneratedEvidenceDocument.objects.all().select_related('planned_document', 'batch').prefetch_related(
        'planned_document__indicators',
        'planned_document__evidence_requirements',
        'planned_document__evidence_requirements__indicator',
    ).order_by('batch__code', 'document_code')
    if selected_batch_id:
        docs_qs = docs_qs.filter(batch_id=selected_batch_id)

    total_generated = GeneratedEvidenceDocument.objects.count()
    docx_available = GeneratedEvidenceDocument.objects.filter(docx_file__isnull=False).exclude(docx_file='').count()
    waiting_signatures = GeneratedEvidenceDocument.objects.filter(docx_status=DOCXStatus.GENERATED_WAITING_APPROVAL).count()
    signed_uploaded = GeneratedEvidenceDocument.objects.filter(linked_evidence_item__isnull=False).count()
    missing_signed_upload = max(docx_available - signed_uploaded, 0)

    indicators = Indicator.objects.all().select_related('evidence_profile')
    ready_indicators = sum(1 for i in indicators if i.calculated_status in [FulfillmentStatus.READY, FulfillmentStatus.VERIFIED])
    partial_indicators = sum(1 for i in indicators if i.calculated_status == FulfillmentStatus.PARTIAL)
    missing_indicators = sum(1 for i in indicators if i.calculated_status == FulfillmentStatus.MISSING)

    import_history = EvidenceItem.objects.filter(generated_source__isnull=False).select_related(
        'uploaded_by',
        'planned_document',
        'planned_document__batch',
    ).prefetch_related('planned_document__indicators').order_by('-created_at')[:200]

    context = {
        'batches': batches,
        'selected_batch_id': int(selected_batch_id) if selected_batch_id and selected_batch_id.isdigit() else None,
        'generated_docs': docs_qs,
        'stats': {
            'total_generated': total_generated,
            'docx_available': docx_available,
            'waiting_signatures': waiting_signatures,
            'signed_uploaded': signed_uploaded,
            'missing_signed_upload': missing_signed_upload,
            'ready_indicators': ready_indicators,
            'partial_indicators': partial_indicators,
            'missing_indicators': missing_indicators,
        },
        'import_history': import_history,
    }
    return render(request, 'evidence/document_transfer_center.html', context)

@login_required
def export_all_generated_docx_zip(request):
    docs = GeneratedEvidenceDocument.objects.filter(docx_file__isnull=False).exclude(docx_file='').select_related('batch').order_by('batch__code', 'document_code')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f"PHC_All_Generated_DOCX_{timestamp}.zip"
    entries = [(f"{d.batch.code}/{os.path.basename(d.docx_file.name)}", d.docx_file) for d in docs if d.docx_file]
    return _build_zip_response(zip_filename, entries)

@login_required
def export_batch_generated_docx_zip(request, batch_id):
    batch = get_object_or_404(DocumentBatch, pk=batch_id)
    docs = GeneratedEvidenceDocument.objects.filter(batch=batch, docx_file__isnull=False).exclude(docx_file='').order_by('document_code')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f"PHC_{batch.code}_DOCX_{timestamp}.zip"
    entries = [(f"{batch.code}/{os.path.basename(d.docx_file.name)}", d.docx_file) for d in docs if d.docx_file]
    return _build_zip_response(zip_filename, entries)

@login_required
def export_selected_generated_docx_zip(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    selected_ids = request.POST.getlist('selected_doc_ids')
    ids = [i for i in selected_ids if str(i).isdigit()]
    docs = GeneratedEvidenceDocument.objects.filter(id__in=ids, docx_file__isnull=False).exclude(docx_file='').select_related('batch')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f"PHC_Selected_DOCX_{timestamp}.zip"
    entries = [(f"{d.batch.code}/{os.path.basename(d.docx_file.name)}", d.docx_file) for d in docs if d.docx_file]
    response = _build_zip_response(zip_filename, entries)
    response['X-Skipped-Count'] = str(max(len(ids) - docs.count(), 0))
    return response

@login_required
def export_document_transfer_manifest_csv(request):
    docs = GeneratedEvidenceDocument.objects.all().select_related('planned_document', 'batch').prefetch_related(
        'planned_document__indicators',
        'planned_document__evidence_requirements',
        'planned_document__evidence_requirements__indicator',
    ).order_by('batch__code', 'document_code')

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow([
        'batch_code',
        'batch_name',
        'planned_document_code',
        'generated_document_id',
        'document_code',
        'document_title',
        'document_kind',
        'linked_indicators',
        'evidence_requirements',
        'docx_available',
        'signed_uploaded',
        'expected_signed_file_name',
        'upload_required',
        'display_required',
        'physical_proof_required',
        'staff_awareness_required',
        'register_required',
        'current_status',
    ])

    for d in docs:
        planned = d.planned_document
        indicators = planned.indicators.all()
        linked_indicators = ';'.join(sorted([i.indicator_no for i in indicators]))

        reqs = planned.evidence_requirements.all()
        req_labels = []
        upload_required = False
        display_required = False
        physical_required = False
        staff_required = False
        register_required = False
        for r in reqs:
            req_labels.append(f"{r.indicator.indicator_no}:{r.title}")
            profile = getattr(r.indicator, 'evidence_profile', None)
            if profile:
                upload_required = upload_required or bool(profile.upload_required)
                display_required = display_required or bool(profile.display_required)
                physical_required = physical_required or bool(profile.physical_proof_required)
                staff_required = staff_required or bool(profile.staff_awareness_required)
                register_required = register_required or bool(profile.register_required)

        safe_kind = getattr(planned, 'document_kind', '') or ''
        expected_signed_file_name = f"{d.document_code}_{d.batch.code}_{safe_kind}_signed.pdf".replace(' ', '_')

        writer.writerow([
            d.batch.code,
            d.batch.name,
            planned.code,
            d.id,
            d.document_code,
            d.title,
            planned.document_kind,
            linked_indicators,
            ';'.join(req_labels),
            bool(d.docx_file),
            bool(d.linked_evidence_item_id),
            expected_signed_file_name,
            upload_required,
            display_required,
            physical_required,
            staff_required,
            register_required,
            d.docx_status,
        ])

    csv_bytes = out.getvalue().encode('utf-8')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    response = HttpResponse(csv_bytes, content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="PHC_Document_Manifest_{timestamp}.csv"'
    return response

@login_required
def upload_signed_document(request, pk):
    doc = get_object_or_404(
        GeneratedEvidenceDocument.objects.select_related('planned_document', 'batch').prefetch_related(
            'planned_document__indicators',
            'planned_document__evidence_requirements',
            'planned_document__evidence_requirements__indicator',
        ),
        pk=pk,
    )
    planned = doc.planned_document
    indicators = planned.indicators.all()
    requirements = planned.evidence_requirements.all()

    if request.method == 'POST':
        form = SignedDocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            evidence_item = EvidenceItem.objects.create(
                title=form.cleaned_data['title'],
                evidence_type=form.cleaned_data['evidence_type'],
                document_type=form.cleaned_data['document_type'],
                file=form.cleaned_data['file'],
                approval_status=form.cleaned_data['approval_status'],
                description=form.cleaned_data.get('remarks') or '',
                uploaded_by=request.user,
                planned_document=planned,
                document_code=doc.document_code,
                version=doc.version,
            )

            for req in requirements:
                EvidenceRequirementFulfillment.objects.get_or_create(
                    evidence_requirement=req,
                    evidence_item=evidence_item,
                    defaults={
                        'status': FulfillmentStatus.PENDING_REVIEW,
                        'physical_confirmed': form.cleaned_data['physical_confirmed'],
                        'display_confirmed': form.cleaned_data['display_confirmed'],
                        'staff_awareness_confirmed': form.cleaned_data['staff_awareness_confirmed'],
                        'register_confirmed': form.cleaned_data['register_confirmed'],
                        'remarks': form.cleaned_data.get('remarks') or '',
                    },
                )

            doc.linked_evidence_item = evidence_item
            doc.status = GeneratedDocumentStatus.SIGNED_UPLOADED
            doc.docx_status = DOCXStatus.SIGNED_UPLOADED
            doc.save(update_fields=['linked_evidence_item', 'status', 'docx_status', 'updated_at'])

            messages.success(request, 'Signed document uploaded and linked to planned document requirements (pending review).')
            return redirect('generated_document_detail', pk=doc.pk)
    else:
        initial_title = f"Signed: {planned.code} - {planned.title}"
        form = SignedDocumentUploadForm(initial={
            'title': initial_title,
            'approval_status': ApprovalStatus.PENDING_REVIEW,
        })

    context = {
        'generated_document': doc,
        'planned_document': planned,
        'indicators': indicators,
        'requirements': requirements,
        'form': form,
    }
    return render(request, 'evidence/upload_signed_document.html', context)

@login_required
def generated_doc_list(request):
    generated_docs = GeneratedEvidenceDocument.objects.all().select_related('planned_document', 'batch').order_by('-generated_at')
    context = {'generated_docs': generated_docs}
    return render(request, 'evidence/generated_doc_list.html', context)

@login_required
def evidence_list(request):
    evidence_items = EvidenceItem.objects.all().order_by('-created_at')
    context = {'evidence_items': evidence_items}
    return render(request, 'evidence/list.html', context)

@login_required
def evidence_add(request):
    planned_doc_id = request.GET.get('planned_document_id')
    planned_doc = None
    if planned_doc_id:
        planned_doc = get_object_or_404(PlannedEvidenceDocument, pk=planned_doc_id)

    if request.method == 'POST':
        form = EvidenceItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.uploaded_by = request.user
            if planned_doc:
                item.planned_document = planned_doc
                # Auto-fill from planned doc if appropriate
                if not item.title:
                    item.title = planned_doc.title
            item.save()
            
            # Pre-link if evidence_requirement id is passed in GET
            req_id = request.GET.get('requirement_id')
            if req_id:
                try:
                    req = EvidenceRequirement.objects.get(pk=req_id)
                    EvidenceRequirementFulfillment.objects.create(
                        evidence_requirement=req,
                        evidence_item=item,
                        status='PENDING_REVIEW'
                    )
                except EvidenceRequirement.DoesNotExist:
                    pass
            
            # If upload from planned document, link to all its mapped requirements
            if planned_doc:
                for req in planned_doc.evidence_requirements.all():
                    EvidenceRequirementFulfillment.objects.get_or_create(
                        evidence_requirement=req,
                        evidence_item=item,
                        defaults={'status': 'PENDING_REVIEW'}
                    )
            
            messages.success(request, 'Evidence added successfully.')
            return redirect('evidence_detail', pk=item.pk)
    else:
        initial = {}
        if planned_doc:
            initial['title'] = planned_doc.title
        form = EvidenceItemForm(initial=initial)
    
    return render(request, 'evidence/add.html', {'form': form, 'planned_doc': planned_doc})

@login_required
def evidence_detail(request, pk):
    item = get_object_or_404(EvidenceItem, pk=pk)
    fulfillments = item.requirement_fulfillments.all()
    context = {
        'evidence': item,
        'fulfillments': fulfillments
    }
    return render(request, 'evidence/detail.html', context)

@login_required
def evidence_link(request, pk):
    item = get_object_or_404(EvidenceItem, pk=pk)
    
    if request.method == 'POST':
        form = EvidenceLinkageForm(request.POST)
        if form.is_valid():
            fulfillment = form.save(commit=False)
            fulfillment.evidence_item = item
            fulfillment.save()
            messages.success(request, 'Evidence linked successfully.')
            return redirect('evidence_detail', pk=item.pk)
    else:
        # If requirement_id is passed, pre-select it
        req_id = request.GET.get('requirement_id')
        initial = {}
        if req_id:
            initial['evidence_requirement'] = req_id
        form = EvidenceLinkageForm(initial=initial)
        
    context = {
        'evidence': item,
        'form': form
    }
    return render(request, 'evidence/link.html', context)

@login_required
def evidence_worklist(request):
    indicators = Indicator.objects.all().select_related('evidence_profile').prefetch_related('planned_documents', 'planned_documents__batch').order_by('indicator_no')
    
    # Filtering Logic
    func_area = request.GET.get('functional_area')
    if func_area:
        indicators = indicators.filter(functional_area_code=func_area)

    # Grouping Logic
    grouped_indicators = {
        'MISSING': [],
        'PARTIAL': [],
        'READY': [],
        'VERIFIED': [],
    }
    for ind in indicators:
        status = ind.calculated_status
        if status in grouped_indicators:
            grouped_indicators[status].append(ind)
            
    context = {
        'grouped_indicators': grouped_indicators,
        'functional_areas': Indicator.objects.values_list('functional_area_code', 'functional_area_name').distinct(),
        'selected_area': func_area,
    }
    return render(request, 'evidence/worklist.html', context)
