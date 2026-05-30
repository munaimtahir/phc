## PHC Lab Compliance Tracker — Copilot Session

**Timestamp (UTC):** 2026-05-22 20:46:13 (20260522_204613)

### 1) Repository inspection summary
- Repo: `/home/munaim/srv/apps/phc`
- Stack: Django app running in Docker Compose (`web` service) with media/docs generation present.
- Current sprint: Build `/evidence/document-transfer/` “Document Pack Import / Export Center” for DOCX export + signed import workflow.

### 2) Execution plan
1. Inspect current models/views/templates relevant to generated docs and evidence uploads.
2. Run baseline checks (Django check, migration check, pytest).
3. Create a timestamped backup snapshot (db/.env/media/generated docs).
4. Implement Document Transfer Center page + navigation links.
5. Implement export endpoints (all/batch/selected ZIP, manifest CSV) and ensure no readiness mutation.
6. Implement/confirm signed upload workflow auto-linking to planned doc, generated doc, indicators, and evidence requirements; add import history view.
7. Add tests; run full suite; run ruff.
8. Write final report + update this session file with outcomes and continuation notes.

### 3) Task checklist
- [ ] Phase 0: Inspect + baseline checks
- [ ] Backup snapshot created
- [ ] `/evidence/document-transfer/` page (tabs/sections + summary cards)
- [ ] Export all DOCX ZIP endpoint
- [ ] Export batch DOCX ZIP endpoint + buttons (transfer page + batch detail)
- [ ] Export selected DOCX ZIP endpoint (POST) + skipped count
- [ ] Individual DOCX download accessible from relevant pages
- [ ] Manifest CSV export endpoint
- [ ] Signed upload (individual) auto-links indicators + evidence requirements
- [ ] Pack-wise upload list implemented (minimum viable)
- [ ] Import history visible (reuse existing evidence records if possible)
- [ ] UI integration links (dashboard + generated docs page, etc.)
- [ ] Tests added/updated and passing
- [ ] Final report written

### 4) Commands run
- `cd /home/munaim/srv/apps/phc && pwd`
- `git status --short`
- `docker compose ps`
- `docker compose logs --tail=100`
- `find . -maxdepth 4 -type f | sort | head -600`
- `sed -n '1,200p' AGENTS.md`
- `sed -n '1,200p' Agent.md`
- `date -u +%Y%m%d_%H%M%S`
- `mkdir -p backups/20260522_204613_before_document_pack_import_export && cp -a db.sqlite3 .env media generated_documents ...`
- `./.venv/bin/pip install -r requirements.txt`
- `./.venv/bin/python manage.py migrate`
- `./.venv/bin/pytest`
- `./.venv/bin/ruff check .`
- `docker compose up -d --build`
- `docker compose exec web python manage.py migrate`
- `docker compose exec web python manage.py check`
- `docker compose exec web python manage.py makemigrations --check --dry-run`
- `docker compose exec web pytest`
- `docker compose exec web ruff check .`
- `curl -I https://phc.alshifalab.pk/evidence/document-transfer/`

### 5) Files changed
- `copilot_session.md` (overwritten at session start)
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
- `core/views.py`
- `core/templates/core/dashboard.html`
- `conftest.py`
- `evidence/test_document_transfer_center.py`
- Various ruff cleanups in management commands and tests

### 6) Tests run
- `docker compose exec web pytest` (pass)
- `docker compose exec web ruff check .` (pass)

### 7) Problems found
- Initial `ruff check .` failures were fixed (unused imports/vars + E701 one-line `if` statements).

### 8) Deployment status
- Docker containers: running (`web` and `phc-accreditation` observed in `docker compose ps`)
- Public URL checks: `https://phc.alshifalab.pk` and `https://phc.alshifalab.pk/evidence/document-transfer/` return `302` to login (expected).

### 9) Continuation notes (if session stops)
- Backup snapshot created: `backups/20260522_204613_before_document_pack_import_export/`.
- Implementation completed. Next sprint: ZIP import with manifest (optional) + explicit readiness-closure workflows for display/physical/staff/register evidence.
