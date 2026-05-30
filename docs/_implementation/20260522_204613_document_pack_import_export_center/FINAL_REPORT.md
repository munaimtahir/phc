# PHC Document Pack Import / Export Center — Final Report

**Timestamp (UTC):** 2026-05-22 20:46:13 (20260522_204613)
**Sprint goal:** Dedicated operational center for exporting generated DOCX drafts and importing signed/finalized evidence without falsely completing readiness.

## 1) Final verdict
**GO**

## 2) What was implemented
- **New operational center page:** `/evidence/document-transfer/` (tabs: Export Documents, Import Signed Documents, Import History, Mapping/Manifest).
- **Export features**
  - Export **all** generated DOCX drafts as ZIP.
  - Export **batch** DOCX drafts as ZIP.
  - Export **selected** DOCX drafts as ZIP (checkbox table).
  - Export **mapping manifest CSV** (document ↔ planned doc ↔ indicators ↔ evidence requirements).
  - Individual DOCX downloads continue to work (`/evidence/generated-documents/<id>/download-docx/`).
- **Import features**
  - **Per-generated-document signed upload** page that auto-links to the planned document, mapped evidence requirements, and indicators.
  - **Pack-wise (batch) import list** (minimum viable): batch filter + per-document “Upload Signed” action.
  - **Import history** view (reuses EvidenceItem linked via `GeneratedEvidenceDocument.linked_evidence_item`).
- **Readiness safety improvements**
  - Added fulfillment-level `register_confirmed` to prevent register-required indicators from becoming READY without explicit confirmation.
  - Upload form defaults confirmations to unchecked (no implicit display/physical/staff awareness/register completion).
- **UI integration**
  - Navbar link: “Documents Import/Export”.
  - Dashboard button: “Document Import/Export Center”.
  - Generated Documents page: quick links for All ZIP + Manifest + Center.
  - Batch detail page: Download batch ZIP + open Center filtered to batch.

## 3) Export summary
- **All ZIP URL:** `/evidence/document-transfer/export/all-docx.zip`
- **Batch ZIP URL:** `/evidence/document-transfer/export/batch/<batch_id>.zip`
- **Selected ZIP URL (POST):** `/evidence/document-transfer/export/selected-docx.zip`
- **Manifest CSV URL:** `/evidence/document-transfer/export/manifest.csv`
- ZIP exports include only generated DOCX drafts (no signed uploads).

## 4) Import summary
- **Upload signed URL:** `/evidence/generated-documents/<id>/upload-signed/`
- Upload creates an `EvidenceItem` and creates `EvidenceRequirementFulfillment` rows for the planned document’s mapped requirements (status `PENDING_REVIEW` by default).
- Generated document is linked to the evidence item via `GeneratedEvidenceDocument.linked_evidence_item`.

## 5) Compliance safety
- Export routes (ZIP/CSV) and DOCX downloads do **not** change indicator readiness.
- Signed upload does **not** auto-confirm display/physical/staff awareness/register requirements; these are explicit checkboxes.
- Register-required profiles now require `register_confirmed=True` on at least one fulfillment for the requirement to become READY.

## 6) Tests
**Commands run (container):**
- `docker compose exec web python manage.py check`
- `docker compose exec web python manage.py makemigrations --check --dry-run`
- `docker compose exec web pytest`
- `docker compose exec web ruff check .`

**Result:** `39 passed` and `ruff` clean.

## 7) Files changed (key)
- `evidence/urls.py`
- `evidence/views.py`
- `evidence/models.py`
- `evidence/forms.py`
- `evidence/migrations/0005_evidencerequirementfulfillment_register_confirmed.py`
- `evidence/templates/evidence/document_transfer_center.html`
- `evidence/templates/evidence/upload_signed_document.html`
- `evidence/templates/evidence/generated_doc_list.html`
- `evidence/templates/evidence/generated_doc_detail.html`
- `evidence/templates/evidence/batch_detail.html`
- `evidence/templates/evidence/planned_doc_detail.html`
- `core/templates/core/dashboard.html`
- `conftest.py`
- `evidence/test_document_transfer_center.py`

## 8) Deployment status
- Containers rebuilt and restarted: `docker compose up -d --build`
- Public URL check:
  - `https://phc.alshifalab.pk` returns `302` to login (expected)
  - `https://phc.alshifalab.pk/evidence/document-transfer/` returns `302` to login (expected)

## 9) Manual user actions required
- Download generated DOCX ZIPs.
- Print/sign documents.
- Upload signed versions per document (or batch-wise list → per-row upload).
- Only check display/physical/staff awareness/register confirmations when truly satisfied.

## 10) Next sprint recommendation
- **Signed Evidence Upload & Readiness Closure Sprint**
  - Add explicit workflows for display/physical/staff awareness/register evidence capture and review/verification.
  - Optional: ZIP import with manifest (with non-overwrite safeguards and unmatched-file reporting).

