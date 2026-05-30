import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User
from indicators.models import Indicator
from evidence.models import EvidenceItem, EvidenceRequirement

@pytest.fixture
def auth_client():
    client = Client()
    User.objects.create_user(username='testuser', password='password')
    client.login(username='testuser', password='password')
    return client

@pytest.fixture
def sample_indicator():
    return Indicator.objects.create(
        indicator_no='IND-TEST-02',
        functional_area_code='TEST',
        standard_no='TEST-1',
        indicator_text='This is a test indicator.'
    )

@pytest.fixture
def sample_requirement(sample_indicator):
    return EvidenceRequirement.objects.create(
        indicator=sample_indicator,
        title='Sample Requirement'
    )

@pytest.fixture
def sample_evidence(auth_client):
    return EvidenceItem.objects.create(
        title='Sample Evidence'
    )

@pytest.mark.django_db
def test_evidence_list_loads(auth_client, sample_evidence):
    response = auth_client.get(reverse('evidence_list'))
    assert response.status_code == 200
    assert b'Sample Evidence' in response.content

@pytest.mark.django_db
def test_evidence_add_loads(auth_client):
    response = auth_client.get(reverse('evidence_add'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_evidence_detail_loads(auth_client, sample_evidence):
    response = auth_client.get(reverse('evidence_detail', args=[sample_evidence.pk]))
    assert response.status_code == 200
    assert b'Sample Evidence' in response.content

@pytest.mark.django_db
def test_evidence_link_loads(auth_client, sample_evidence):
    response = auth_client.get(reverse('evidence_link', args=[sample_evidence.pk]))
    assert response.status_code == 200
