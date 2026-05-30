import pytest
import os
from django.core.management import call_command
from django.urls import reverse
from evidence.models import GeneratedEvidenceDocument
from core.constants import DOCXStatus

@pytest.fixture(scope='function')
def seed_data():
    call_command('import_phc_indicators', 'data/source_materials/test-export_framework_template_FIXED.csv')
    call_command('bootstrap_evidence_requirements')
    call_command('seed_document_batches')
    call_command('generate_document_pack', '--batch', 'GOV')

@pytest.fixture
def auth_client():
    from django.test import Client
    from django.contrib.auth.models import User
    client = Client()
    User.objects.create_user(username='testuser', password='password')
    client.login(username='testuser', password='password')
    return client

@pytest.mark.django_db
def test_generate_docx_command_works(seed_data):
    doc = GeneratedEvidenceDocument.objects.first()
    assert doc.docx_status == DOCXStatus.NOT_GENERATED
    
    call_command('generate_docx_documents', '--only', str(doc.id))
    
    doc.refresh_from_db()
    assert doc.docx_status == DOCXStatus.GENERATED_WAITING_APPROVAL
    assert doc.docx_file.name.endswith('.docx')
    assert os.path.exists(doc.docx_file.path)

@pytest.mark.django_db
def test_download_docx_view(auth_client, seed_data):
    doc = GeneratedEvidenceDocument.objects.first()
    call_command('generate_docx_documents', '--only', str(doc.id))
    
    url = reverse('download_docx', args=[doc.id])
    response = auth_client.get(url)
    
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    assert 'attachment' in response['Content-Disposition']

@pytest.mark.django_db
def test_docx_generation_preserves_indicator_readiness(seed_data):
    # This test ensures that generating a DOCX doesn't falsely mark an indicator as ready
    doc = GeneratedEvidenceDocument.objects.get(document_code='DOC-GOV-01') # Mission Statement
    indicator = doc.planned_document.indicators.first()
    
    from core.constants import FulfillmentStatus
    assert indicator.calculated_status == FulfillmentStatus.MISSING
    
    call_command('generate_docx_documents', '--only', str(doc.id))
    
    indicator.refresh_from_db()
    assert indicator.calculated_status == FulfillmentStatus.MISSING
