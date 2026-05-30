import pytest
from io import StringIO
from django.core.management import call_command
from indicators.models import Indicator
from evidence.models import IndicatorEvidenceProfile, EvidenceRequirementFulfillment, EvidenceItem
from core.constants import PrimaryEvidenceType, RecurrenceFrequency, FulfillmentStatus

@pytest.fixture(scope='function')
def seed_initial_data(django_db_setup, django_db_blocker):
    """Ensure the database is seeded with indicators and requirements for each test."""
    with django_db_blocker.unblock():
        call_command('migrate')
        call_command('import_phc_indicators', 'data/source_materials/test-export_framework_template_FIXED.csv')
        call_command('bootstrap_evidence_requirements')

@pytest.mark.django_db(transaction=True)
def test_seed_profiles_is_idempotent(seed_initial_data):
    out = StringIO()
    call_command('seed_evidence_profiles', stdout=out)
    assert "Created: 118" in out.getvalue()
    
    out = StringIO()
    call_command('seed_evidence_profiles', stdout=out)
    assert "Skipped: 118" in out.getvalue()
    
    assert IndicatorEvidenceProfile.objects.count() == 118

@pytest.mark.django_db(transaction=True)
def test_ind_007_mission_statement_profile(seed_initial_data):
    call_command('seed_evidence_profiles', '--update')
    indicator = Indicator.objects.get(indicator_no='IND-007')
    profile = indicator.evidence_profile
    assert profile.primary_evidence_type == PrimaryEvidenceType.DISPLAY_NOTICE
    assert profile.upload_required is True
    assert profile.display_required is True
    assert profile.physical_proof_required is True
    assert profile.approval_required is True

@pytest.mark.django_db(transaction=True)
def test_ind_116_complaint_register_profile(seed_initial_data):
    call_command('seed_evidence_profiles', '--update')
    indicator = Indicator.objects.get(indicator_no='IND-116')
    profile = indicator.evidence_profile
    assert profile.primary_evidence_type == PrimaryEvidenceType.REGISTER_LOGBOOK
    assert profile.register_required is True
    assert profile.recurrence_frequency == RecurrenceFrequency.MONTHLY

@pytest.mark.django_db(transaction=True)
def test_readiness_logic_with_profiles(seed_initial_data):
    call_command('seed_evidence_profiles', '--update')
    indicator = Indicator.objects.get(indicator_no='IND-007') # Mission Statement
    requirement = indicator.evidence_requirements.first()
    
    # Status is MISSING initially
    assert requirement.status == FulfillmentStatus.MISSING
    assert indicator.calculated_status == FulfillmentStatus.MISSING

    # Create an evidence item and link it
    item = EvidenceItem.objects.create(title='Mission Statement Doc')
    fulfillment = EvidenceRequirementFulfillment.objects.create(
        evidence_requirement=requirement,
        evidence_item=item
    )
    
    # Status is now PARTIAL because confirmations are missing
    assert requirement.status == FulfillmentStatus.PARTIAL
    assert indicator.calculated_status == FulfillmentStatus.PARTIAL
    
    # Confirm physical and display proof
    fulfillment.physical_confirmed = True
    fulfillment.display_confirmed = True
    fulfillment.save()
    
    # Status is now READY because confirmations are met
    assert requirement.status == FulfillmentStatus.READY
    assert indicator.calculated_status == FulfillmentStatus.READY
    
    # Verify the fulfillment
    fulfillment.status = FulfillmentStatus.VERIFIED
    fulfillment.save()
    
    # Status is now VERIFIED
    assert requirement.status == FulfillmentStatus.VERIFIED
    assert indicator.calculated_status == FulfillmentStatus.VERIFIED
