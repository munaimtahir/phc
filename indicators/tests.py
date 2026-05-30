import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User
from indicators.models import Indicator
from evidence.models import EvidenceRequirement

@pytest.fixture
def auth_client():
    client = Client()
    User.objects.create_user(username='testuser', password='password')
    client.login(username='testuser', password='password')
    return client

@pytest.fixture
def sample_indicator():
    return Indicator.objects.create(
        indicator_no='IND-TEST-01',
        functional_area_code='TEST',
        standard_no='TEST-1',
        indicator_text='This is a test indicator.'
    )

@pytest.fixture
def sample_requirement(sample_indicator):
    return EvidenceRequirement.objects.create(
        indicator=sample_indicator,
        title='Sample Requirement Title'
    )

@pytest.mark.django_db
def test_indicator_list_loads(auth_client, sample_indicator):
    response = auth_client.get(reverse('indicator_list'))
    assert response.status_code == 200
    assert b'IND-TEST-01' in response.content

@pytest.mark.django_db
def test_indicator_detail_loads(auth_client, sample_indicator):
    response = auth_client.get(reverse('indicator_detail', args=[sample_indicator.pk]))
    assert response.status_code == 200
    assert b'This is a test indicator.' in response.content
    assert b'Evidence Requirements' in response.content

@pytest.mark.django_db
def test_generate_prompt_view_loads(auth_client, sample_indicator, sample_requirement):
    response = auth_client.get(reverse('generate_prompt', args=[sample_indicator.pk, sample_requirement.pk]))
    assert response.status_code == 200
    assert b'Al Shifa Laboratory' in response.content
    assert b'IND-TEST-01' in response.content
    assert b'Sample Requirement Title' in response.content

@pytest.mark.django_db
def test_generate_prompt_view_downloads(auth_client, sample_indicator, sample_requirement):
    response = auth_client.get(reverse('generate_prompt', args=[sample_indicator.pk, sample_requirement.pk]) + '?download=1')
    assert response.status_code == 200
    assert response['Content-Disposition'] == f'attachment; filename="prompt_IND-TEST-01_{sample_requirement.pk}.txt"'
    assert b'Al Shifa Laboratory' in response.content
