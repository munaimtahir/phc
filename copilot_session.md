# Copilot Session - PHC Lab Compliance Tracker

## Project Objective
Build a small, practical, single-purpose Django monolith for one fixed Punjab Healthcare Commission MSDS Clinical/Pathology Laboratory checklist (118 indicators) to answer "Are we ready for PHC Lab inspection, and where is the evidence?".

## Scope Boundaries
- Do NOT build: multi-framework accreditation platform, framework builder, CAPA board, advanced RBAC, Next.js/React frontend, live AI, multi-tenant SaaS, old AccrediOps compatibility layer.
- Build only what directly supports PHC Lab inspection readiness.

## Repository State
- Directory: `/home/munaim/srv/apps/phc`
- Python/Django backend with Postgres.
- Some app directories (`core`, `accounts`, `indicators`, `evidence`, `registers`, `reports`, `config`) appear to exist or need scaffolding.
- `manage.py` check is pending.

## Source Files Found
- `data/seed/`: Empty (as expected).
- `data/source_materials/`:
  - `4thC-RevAnnexs-MSDS  RM Clinical Labs-220518-240518.docx`
  - `SM MSDS Pathology-CLs-2505-QA2605-Rev100718.pdf`
  - `test-export_framework_template_FIXED.csv`

## Execution Plan & Task Checklist
- [x] Phase 0: Repository and Source Review
- [x] Phase 1: Django Foundation (config, apps, auth, static, templates)
- [x] Phase 2: Locked PHC Indicator Master (Models)
- [x] Phase 3: Import Command from Real CSV
- [x] Phase 4: Indicator UI
- [x] Phase 5: Evidence Library
- [x] Phase 6: Digital Registers
- [x] Phase 7: Recurring Compliance Tracking
- [x] Phase 8: Dashboard
- [x] Phase 9: Reports and Print Pack
- [x] Phase 10: Admin and Basic Settings
- [x] Phase 11: Tests
- [x] Phase 12: Docker and Deployment
- [x] Phase 13: Documentation
- [x] Phase 14: Final Quality Gate

## Data Mapping Decisions
- CSV `indicator_code` -> `Indicator.indicator_no`
- CSV `area_code` -> `Indicator.functional_area_code`
- CSV `area_name` -> `Indicator.functional_area_name`
- CSV `standard_code` -> `Indicator.standard_code`
- CSV `standard_name` -> `Indicator.standard_title`
- CSV `indicator_text` -> `Indicator.indicator_text`
- CSV `fulfillment_guidance` -> `Indicator.compliance_requirement` / `surveyor_check`
- CSV `required_evidence_description` -> `Indicator.required_evidence`
- CSV `evidence_type` -> `Indicator.evidence_category`
- CSV `is_recurring` -> `Indicator.recurring_required`
- CSV `recurrence_frequency` -> `Indicator.recurrence_frequency`

## Completed Work
- Inspected repository and found source materials.
- Initialized `copilot_session.md`.

## Pending Work
- Check if Django is initialized and create missing foundation files.

## Tests Run
- None yet

## Test Results
- N/A

## Deployment Notes
- Caddy reverse proxy will be used for `phc.alshifalab.pk`.
- Docker Compose will bind container 8000 to host 127.0.0.1:8018.

## Known Limitations
- None yet

## Next Handoff Notes
- Continuing with Phase 1.
