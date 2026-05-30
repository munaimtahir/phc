import io
import zipfile

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from core.constants import ApprovalStatus, FulfillmentStatus
from evidence.models import (
    DocumentBatch,
    EvidenceRequirement,
    EvidenceRequirementFulfillment,
    GeneratedEvidenceDocument,
    IndicatorEvidenceProfile,
    PlannedEvidenceDocument,
)
from indicators.models import Indicator


@pytest.fixture
def auth_client(db):
    from django.test import Client
    from django.contrib.auth.models import User

    client = Client()
    User.objects.create_user(username="testuser", password="password")
    client.login(username="testuser", password="password")
    return client


@pytest.mark.django_db
def test_document_transfer_center_loads(auth_client):
    response = auth_client.get(reverse("document_transfer_center"))
    assert response.status_code == 200
    assert b"Document Pack Import / Export Center" in response.content


@pytest.mark.django_db
def test_manifest_csv_exports(auth_client):
    batch = DocumentBatch.objects.create(name="Governance", code="GOV")
    ind = Indicator.objects.create(
        indicator_no="IND-900",
        functional_area_code="GOV",
        functional_area_name="Governance",
        standard_no="STD-1",
        standard_code="STD-1",
        standard_title="Test",
        indicator_text="Test indicator",
    )
    IndicatorEvidenceProfile.objects.create(indicator=ind, upload_required=True)
    req = EvidenceRequirement.objects.create(indicator=ind, title="Requirement A")

    planned = PlannedEvidenceDocument.objects.create(title="Doc", code="DOC-PL-1", batch=batch)
    planned.indicators.add(ind)
    planned.evidence_requirements.add(req)

    GeneratedEvidenceDocument.objects.create(
        planned_document=planned,
        batch=batch,
        title="Generated",
        document_code="DOC-GEN-1",
        content_markdown="x",
    )

    response = auth_client.get(reverse("export_document_transfer_manifest_csv"))
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/csv")
    assert b"document_code" in response.content
    assert b"DOC-GEN-1" in response.content


@pytest.mark.django_db
def test_export_selected_zip_returns_zip(auth_client, settings, tmp_path):
    batch = DocumentBatch.objects.create(name="Governance", code="GOV")
    ind = Indicator.objects.create(
        indicator_no="IND-901",
        functional_area_code="GOV",
        functional_area_name="Governance",
        standard_no="STD-1",
        standard_code="STD-1",
        standard_title="Test",
        indicator_text="Test indicator",
    )
    planned = PlannedEvidenceDocument.objects.create(title="Doc", code="DOC-PL-2", batch=batch)
    planned.indicators.add(ind)

    # Create a fake docx on disk and point FileField to it
    fake_docx_dir = tmp_path / "generated_documents_docx" / "GOV" / "t"
    fake_docx_dir.mkdir(parents=True)
    fake_docx_path = fake_docx_dir / "DOC-GEN-2_Test.docx"
    fake_docx_path.write_bytes(b"fake-docx")

    settings.MEDIA_ROOT = str(tmp_path)

    gen = GeneratedEvidenceDocument.objects.create(
        planned_document=planned,
        batch=batch,
        title="Generated",
        document_code="DOC-GEN-2",
        content_markdown="x",
    )
    gen.docx_file.name = str(fake_docx_path.relative_to(tmp_path))
    gen.save(update_fields=["docx_file"])

    response = auth_client.post(
        reverse("export_selected_generated_docx_zip"),
        data={"selected_doc_ids": [str(gen.id)]},
    )
    assert response.status_code == 200
    assert response["Content-Type"] == "application/zip"

    zip_bytes = b"".join(response.streaming_content)
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        names = zf.namelist()
        assert any(n.endswith(".docx") for n in names)


@pytest.mark.django_db
def test_upload_signed_creates_fulfillments_without_auto_confirm(auth_client):
    batch = DocumentBatch.objects.create(name="Governance", code="GOV")
    ind = Indicator.objects.create(
        indicator_no="IND-902",
        functional_area_code="GOV",
        functional_area_name="Governance",
        standard_no="STD-1",
        standard_code="STD-1",
        standard_title="Test",
        indicator_text="Test indicator",
    )
    IndicatorEvidenceProfile.objects.create(indicator=ind, upload_required=True, register_required=True)
    req = EvidenceRequirement.objects.create(indicator=ind, title="Requirement A")

    planned = PlannedEvidenceDocument.objects.create(title="Doc", code="DOC-PL-3", batch=batch)
    planned.indicators.add(ind)
    planned.evidence_requirements.add(req)

    gen = GeneratedEvidenceDocument.objects.create(
        planned_document=planned,
        batch=batch,
        title="Generated",
        document_code="DOC-GEN-3",
        content_markdown="x",
    )

    upload = SimpleUploadedFile("signed.pdf", b"pdf-bytes", content_type="application/pdf")
    response = auth_client.post(
        reverse("upload_signed_document", args=[gen.id]),
        data={
            "title": "Signed: Doc",
            "evidence_type": "CONTROLLED_DOCUMENT",
            "document_type": "SOP",
            "approval_status": ApprovalStatus.PENDING_REVIEW,
            "remarks": "Uploaded",
            "file": upload,
        },
    )
    assert response.status_code == 302

    gen.refresh_from_db()
    assert gen.linked_evidence_item_id is not None

    fulfillment = EvidenceRequirementFulfillment.objects.get(evidence_requirement=req, evidence_item=gen.linked_evidence_item)
    assert fulfillment.status == FulfillmentStatus.PENDING_REVIEW
    assert fulfillment.register_confirmed is False

    # Because register is required but not confirmed, requirement should not be READY.
    req.refresh_from_db()
    assert req.status in [FulfillmentStatus.MISSING, FulfillmentStatus.PARTIAL]

