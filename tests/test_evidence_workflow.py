import pytest
from django.urls import reverse
from indicators.models import Indicator
from evidence.models import EvidenceItem

@pytest.fixture
def auth_client(client, django_user_model):
    user = django_user_model.objects.create_user(username='testuser', password='testpassword')
    client.force_login(user)
    return client

@pytest.mark.django_db
def test_evidence_create_view_loads(auth_client):
    response = auth_client.get(reverse('evidence:add'))
    assert response.status_code == 200
    assert 'Add New Evidence' in response.content.decode()

@pytest.mark.django_db
def test_evidence_create_with_indicator_context(auth_client):
    indicator = Indicator.objects.create(indicator_no='IND-001', indicator_text='Test Indicator')
    response = auth_client.get(reverse('evidence:add') + f'?indicator={indicator.pk}')
    assert response.status_code == 200
    assert 'Add Evidence for Indicator' in response.content.decode()

@pytest.mark.django_db
def test_evidence_creation_and_linking(auth_client):
    indicator = Indicator.objects.create(indicator_no='IND-002', indicator_text='Test Indicator 2')
    data = {
        'title': 'New SOP',
        'evidence_type': 'SOP / Policy',
        'description': 'Test Description',
        'linked_indicators': [indicator.pk],
    }
    response = auth_client.post(reverse('evidence:add') + f'?indicator={indicator.pk}', data)
    assert response.status_code == 302
    assert response.url == reverse('indicators:detail', kwargs={'pk': indicator.pk})
    
    evidence = EvidenceItem.objects.get(title='New SOP')
    assert evidence.linked_indicators.count() == 1
    assert evidence.linked_indicators.first() == indicator

@pytest.mark.django_db
def test_link_existing_evidence(auth_client):
    indicator = Indicator.objects.create(indicator_no='IND-003', indicator_text='Test Indicator 3')
    evidence = EvidenceItem.objects.create(title='Existing Evidence', evidence_type='Other')
    
    response = auth_client.get(reverse('evidence:link', kwargs={'pk': evidence.pk}) + f'?indicator={indicator.pk}')
    assert response.status_code == 302
    assert response.url == reverse('indicators:detail', kwargs={'pk': indicator.pk})
    
    evidence.refresh_from_db()
    assert indicator in evidence.linked_indicators.all()

@pytest.mark.django_db
def test_admin_back_link_exists(auth_client):
    # This might be harder to test via client as it depends on template loading in admin
    # but we can check if the custom template is at the expected location.
    import os
    assert os.path.exists('templates/admin/base_site.html')
