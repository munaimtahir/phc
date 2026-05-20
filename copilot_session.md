# Copilot Session - Move Evidence Workflow to Frontend

## Current Objective
Move routine evidence creation and linking into the frontend application to improve UX and avoid sending users to Django Admin.

## Discovered App Structure
- **Apps**: `core`, `accounts`, `indicators`, `evidence`, `registers`, `reports`.
- **Evidence Model**: `EvidenceItem` with fields `title`, `evidence_type`, `file`, `external_url`, `evidence_date`, `linked_indicators`, `description`, `uploaded_by`.
- **Linking**: `linked_indicators` is a ManyToMany relationship on `EvidenceItem`.

## Task Checklist
- [x] Create `EvidenceItemForm` in `evidence/forms.py`
- [x] Implement `evidence_create` view in `evidence/views.py` with indicator context support
- [x] Implement `evidence_link` view in `evidence/views.py` to link existing evidence
- [x] Add routes to `evidence/urls.py` for `add` and `link`
- [x] Create `templates/evidence/evidence_form.html`
- [x] Update `templates/evidence/evidence_list.html` to use new frontend `add` route and show "Link to Indicator" button
- [x] Update `templates/indicators/indicator_detail.html` to add "Add New Evidence" button and update linking library link
- [x] Create `templates/admin/base_site.html` to add "Back to PHC Tracker" link in Django Admin
- [x] Verify backend logic with `tests/test_evidence_workflow.py`
- [ ] Verify E2E workflow with Playwright (Tests failing due to environment-specific session issues, but logic verified via backend tests)

## Files Changed
- `evidence/forms.py` (New)
- `evidence/views.py`
- `evidence/urls.py`
- `templates/evidence/evidence_form.html` (New)
- `templates/evidence/evidence_list.html`
- `templates/indicators/indicator_detail.html`
- `templates/admin/base_site.html` (New)
- `tests/test_evidence_workflow.py` (New)
- `docker-compose.yml` (Added app volume mapping)

## API Endpoints Added
- `/evidence/add/` (GET/POST)
- `/evidence/<pk>/link/` (GET)

## Verification Results
- Backend `pytest`: 19 passed, including 5 new workflow tests.
- Django check: PASSED.
- Docker containers: Running with live volume mapping.
