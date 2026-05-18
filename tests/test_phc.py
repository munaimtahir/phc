import pytest
from django.urls import reverse
from indicators.models import Indicator, IndicatorCompliance
from evidence.models import EvidenceItem
from registers.models import RegisterDefinition, RegisterEntry

@pytest.fixture
def auth_client(client, django_user_model):
    user = django_user_model.objects.create_user(username='testuser', password='testpassword')
    client.force_login(user)
    return client

@pytest.mark.django_db
def test_health_check(client):
    response = client.get(reverse('health'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_dashboard_authenticated(auth_client):
    response = auth_client.get(reverse('dashboard'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_dashboard_unauthenticated(client):
    response = client.get(reverse('dashboard'))
    assert response.status_code == 302
    assert '/accounts/login/' in response.url

@pytest.mark.django_db
def test_indicator_models():
    indicator = Indicator.objects.create(indicator_no='TEST-01', max_score=10)
    compliance = IndicatorCompliance.objects.create(indicator=indicator, evidence_status='ready')
    assert compliance.current_score == 10
    
    compliance.evidence_status = 'missing'
    compliance.save()
    assert compliance.current_score == 0

@pytest.mark.django_db
def test_evidence_item(auth_client):
    indicator = Indicator.objects.create(indicator_no='TEST-02')
    ev = EvidenceItem.objects.create(title='Test Evidence', evidence_type='SOP / Policy')
    ev.linked_indicators.add(indicator)
    
    assert ev.linked_indicators.count() == 1
    assert ev.linked_indicators.first().indicator_no == 'TEST-02'

@pytest.mark.django_db
def test_register_definition():
    reg = RegisterDefinition.objects.create(name='Test Register', frequency='Daily')
    # Since there are no entries, last_entry_date should be None
    assert reg.last_entry_date is None
    assert reg.next_due_date is None
    assert reg.is_overdue is False
    assert reg.is_due_soon is False
    
    # Add an entry for yesterday
    import datetime
    from dateutil.relativedelta import relativedelta
    yesterday = datetime.date.today() - relativedelta(days=1)
    
    RegisterEntry.objects.create(
        register_definition=reg,
        entry_date=yesterday,
        values_json={'field_note': 'Test'}
    )
    
    # Reload from DB logic handled by property
    assert reg.last_entry_date == yesterday
    assert reg.next_due_date == yesterday + datetime.timedelta(days=1) # which is today
    assert reg.is_overdue is False # Due today is not overdue
    assert reg.is_due_soon is True # Due today is due soon

@pytest.mark.django_db
def test_report_pages(auth_client):
    assert auth_client.get(reverse('reports:score_summary')).status_code == 200
    assert auth_client.get(reverse('reports:missing_evidence')).status_code == 200
    assert auth_client.get(reverse('reports:surveyor_pack')).status_code == 200

@pytest.mark.django_db
def test_printable_register_page(auth_client):
    reg = RegisterDefinition.objects.create(name='Test Register', frequency='Daily')
    response = auth_client.get(reverse('registers:detail', kwargs={'pk': reg.pk}))
    assert response.status_code == 200
