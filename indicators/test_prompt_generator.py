import pytest

from indicators.models import Indicator, IndicatorCompliance
from indicators.services.prompt_generator import (
    PROMPT_TYPE_GAP_ACTION_PLAN,
    PROMPT_TYPE_REGISTER,
    PROMPT_TYPE_SOP_POLICY,
    build_prompt,
)


@pytest.fixture
def indicator_with_compliance(db):
    indicator = Indicator.objects.create(
        indicator_no='IND-001',
        functional_area_code='LAB',
        functional_area_name='Laboratory Management',
        standard_code='STD-1',
        standard_title='Quality',
        indicator_text='Ensure SOPs are available.',
        compliance_requirement='SOP must be documented and signed.',
        required_evidence='Signed SOP copy',
        register_required=True,
        register_name='SOP Control Register',
        recurring_required=True,
        recurrence_frequency='Monthly',
    )
    IndicatorCompliance.objects.create(
        indicator=indicator,
        evidence_status='partial',
        gap_summary='Approval signature missing.',
        next_action='Get consultant signature.',
    )
    return indicator


@pytest.mark.django_db
def test_prompt_generator_includes_lab_name(indicator_with_compliance):
    prompt = build_prompt(indicator_with_compliance, PROMPT_TYPE_SOP_POLICY)
    assert 'Al Shifa Laboratory' in prompt


@pytest.mark.django_db
def test_prompt_generator_includes_indicator_number(indicator_with_compliance):
    prompt = build_prompt(indicator_with_compliance, PROMPT_TYPE_SOP_POLICY)
    assert 'Indicator number: IND-001' in prompt


@pytest.mark.django_db
def test_sop_prompt_includes_approval_section(indicator_with_compliance):
    prompt = build_prompt(indicator_with_compliance, PROMPT_TYPE_SOP_POLICY)
    assert 'Approval section should include:' in prompt
    assert 'Prepared by: Dr. Muhammad Munaim Tahir' in prompt


@pytest.mark.django_db
def test_register_prompt_includes_frequency_and_register_name(indicator_with_compliance):
    prompt = build_prompt(indicator_with_compliance, PROMPT_TYPE_REGISTER)
    assert 'Register name: SOP Control Register' in prompt
    assert 'Frequency: Monthly' in prompt


@pytest.mark.django_db
def test_gap_prompt_includes_current_gap(indicator_with_compliance):
    prompt = build_prompt(indicator_with_compliance, PROMPT_TYPE_GAP_ACTION_PLAN)
    assert 'Current gap: Approval signature missing.' in prompt


@pytest.mark.django_db
def test_prompt_generation_with_blank_optional_fields_does_not_crash(db):
    indicator = Indicator.objects.create(
        indicator_no='IND-002',
        indicator_text='Minimal indicator text',
    )
    IndicatorCompliance.objects.create(indicator=indicator)

    prompt = build_prompt(indicator, PROMPT_TYPE_SOP_POLICY)
    assert 'Not specified in tracker.' in prompt
