import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User
from registers.models import RegisterDefinition

@pytest.fixture
def auth_client():
    client = Client()
    User.objects.create_user(username='testuser', password='password')
    client.login(username='testuser', password='password')
    return client

@pytest.fixture
def sample_register():
    return RegisterDefinition.objects.create(
        name='Temperature Log',
        category='General'
    )

@pytest.mark.django_db
def test_register_list_loads(auth_client, sample_register):
    response = auth_client.get(reverse('register_list'))
    assert response.status_code == 200
    assert b'Temperature Log' in response.content

@pytest.mark.django_db
def test_register_detail_loads(auth_client, sample_register):
    response = auth_client.get(reverse('register_detail', args=[sample_register.pk]))
    assert response.status_code == 200
    assert b'Temperature Log' in response.content

@pytest.mark.django_db
def test_add_entry_loads(auth_client, sample_register):
    response = auth_client.get(reverse('register_entry_add', args=[sample_register.pk]))
    assert response.status_code == 200

@pytest.mark.django_db
def test_register_print_loads(auth_client, sample_register):
    response = auth_client.get(reverse('register_print', args=[sample_register.pk]))
    assert response.status_code == 200
    assert b'Temperature Log' in response.content
