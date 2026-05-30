import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_health_check_returns_200():
    client = Client()
    response = client.get(reverse('health_check'))
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}

@pytest.mark.django_db
def test_dashboard_requires_login():
    client = Client()
    response = client.get(reverse('dashboard'))
    assert response.status_code == 302
    assert response.url.startswith(reverse('login'))

@pytest.mark.django_db
def test_dashboard_loads_for_authenticated_user():
    client = Client()
    User.objects.create_user(username='testuser', password='password')
    client.login(username='testuser', password='password')
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert b'PHC Lab Compliance Dashboard' in response.content
