import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

@pytest.fixture
def auth_client():
    client = Client()
    User.objects.create_user(username='testuser', password='password')
    client.login(username='testuser', password='password')
    return client

@pytest.mark.django_db
def test_reports_home_loads(auth_client):
    response = auth_client.get(reverse('reports_home'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_score_summary_loads(auth_client):
    response = auth_client.get(reverse('report_score_summary'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_missing_evidence_loads(auth_client):
    response = auth_client.get(reverse('report_missing_evidence'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_evidence_index_loads(auth_client):
    response = auth_client.get(reverse('report_evidence_index'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_recurring_loads(auth_client):
    response = auth_client.get(reverse('report_recurring'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_surveyor_pack_loads(auth_client):
    response = auth_client.get(reverse('report_surveyor_pack'))
    assert response.status_code == 200
