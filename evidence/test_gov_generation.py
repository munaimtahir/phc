import pytest
from django.core.management import call_command
from evidence.models import GeneratedEvidenceDocument
from indicators.models import Indicator

@pytest.fixture(scope='function')
def seed_data():
    call_command('import_phc_indicators', 'data/source_materials/test-export_framework_template_FIXED.csv')
    call_command('bootstrap_evidence_requirements')
    call_command('seed_document_batches')

@pytest.mark.django_db
def test_generate_gov_pack_creates_drafts(seed_data):
    call_command('generate_gov_pack')
    
    # Verify records in DB
    assert GeneratedEvidenceDocument.objects.count() == 28
    
    # Verify specific doc
    doc = GeneratedEvidenceDocument.objects.get(document_code='DOC-GOV-01')
    assert "Mission Statement" in doc.title
    assert "Al Shifa Laboratory" in doc.content_markdown
    assert "IND-007" in doc.content_markdown

@pytest.mark.django_db
def test_generate_gov_pack_only_option(seed_data):
    call_command('generate_gov_pack', '--only', 'DOC-GOV-01')
    assert GeneratedEvidenceDocument.objects.count() == 1
    assert GeneratedEvidenceDocument.objects.filter(document_code='DOC-GOV-01').exists()

@pytest.mark.django_db
def test_draft_does_not_mark_indicator_ready(seed_data):
    call_command('generate_gov_pack', '--only', 'DOC-GOV-01')
    indicator = Indicator.objects.get(indicator_no='IND-007')
    # Status should still be MISSING because no real evidence uploaded
    from core.constants import FulfillmentStatus
    assert indicator.calculated_status == FulfillmentStatus.MISSING

@pytest.fixture
def auth_client():
    from django.test import Client
    from django.contrib.auth.models import User
    client = Client()
    User.objects.create_user(username='testuser', password='password')
    client.login(username='testuser', password='password')
    return client

@pytest.mark.django_db
def test_generated_document_list_returns_200(auth_client, seed_data):
    call_command('generate_gov_pack', '--only', 'DOC-GOV-01')
    from django.urls import reverse
    response = auth_client.get(reverse('generated_document_list'))
    assert response.status_code == 200
    assert b'DOC-GOV-01' in response.content

@pytest.mark.django_db
def test_generated_document_detail_returns_200(auth_client, seed_data):
    call_command('generate_gov_pack', '--only', 'DOC-GOV-01')
    from django.urls import reverse
    doc = GeneratedEvidenceDocument.objects.get(document_code='DOC-GOV-01')
    response = auth_client.get(reverse('generated_document_detail', args=[doc.pk]))
    assert response.status_code == 200
    assert b'Mission Statement' in response.content
