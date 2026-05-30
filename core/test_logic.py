import pytest
from indicators.models import Indicator
from evidence.models import EvidenceRequirement, EvidenceRequirementFulfillment, EvidenceItem, IndicatorEvidenceProfile
from core.constants import FulfillmentStatus, PrimaryEvidenceType

@pytest.mark.django_db
def test_evidence_requirement_status_logic():
    ind = Indicator.objects.create(indicator_no='T1', indicator_text='Test')
    # Create profile requiring upload AND physical proof
    IndicatorEvidenceProfile.objects.create(
        indicator=ind, primary_evidence_type=PrimaryEvidenceType.OTHER, 
        upload_required=True, physical_proof_required=True
    )
    req = EvidenceRequirement.objects.create(indicator=ind, title='R1', minimum_required_count=1)
    
    # Missing
    assert req.status == FulfillmentStatus.MISSING
    
    # Partial (only upload provided, but physical proof still needed)
    item = EvidenceItem.objects.create(title='E1')
    f1 = EvidenceRequirementFulfillment.objects.create(evidence_requirement=req, evidence_item=item, status=FulfillmentStatus.DRAFT)
    assert req.status == FulfillmentStatus.PARTIAL
    
    # Ready (now confirm physical proof)
    f1.physical_confirmed = True
    f1.save()
    assert req.status == FulfillmentStatus.READY
    
    # Verified
    f1.status = FulfillmentStatus.VERIFIED
    f1.save()
    assert req.status == FulfillmentStatus.VERIFIED

@pytest.mark.django_db
def test_indicator_readiness_logic():
    ind = Indicator.objects.create(indicator_no='T2', indicator_text='Test', max_score=10)
    IndicatorEvidenceProfile.objects.create(indicator=ind, primary_evidence_type=PrimaryEvidenceType.OTHER, upload_required=True)
    req1 = EvidenceRequirement.objects.create(indicator=ind, title='R1', minimum_required_count=1)
    req2 = EvidenceRequirement.objects.create(indicator=ind, title='R2', minimum_required_count=1)
    
    # Both missing
    assert ind.calculated_status == FulfillmentStatus.MISSING
    assert ind.score == 0
    
    # One ready (only upload needed), one missing
    item = EvidenceItem.objects.create(title='E1')
    EvidenceRequirementFulfillment.objects.create(evidence_requirement=req1, evidence_item=item, status=FulfillmentStatus.DRAFT)
    assert ind.calculated_status == FulfillmentStatus.PARTIAL # because req2 is missing
    
    # Both ready
    item2 = EvidenceItem.objects.create(title='E2')
    EvidenceRequirementFulfillment.objects.create(evidence_requirement=req2, evidence_item=item2, status=FulfillmentStatus.READY)
    assert ind.calculated_status == FulfillmentStatus.READY
    assert ind.score == 10
    
    # One verified, one ready
    f1 = EvidenceRequirementFulfillment.objects.get(evidence_requirement=req1)
    f1.status = FulfillmentStatus.VERIFIED
    f1.save()
    assert ind.calculated_status == FulfillmentStatus.READY # All must be verified for VERIFIED
    
    # Both verified
    f2 = EvidenceRequirementFulfillment.objects.get(evidence_requirement=req2)
    f2.status = FulfillmentStatus.VERIFIED
    f2.save()
    assert ind.calculated_status == FulfillmentStatus.VERIFIED
    assert ind.score == 10
