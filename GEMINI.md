# GEMINI.md

## Project Identity

Repository/folder name: `phc`

Product name: **PHC Lab Compliance Tracker**

Deployment target:

- Server path: `/home/munaim/srv/apps/phc`
- Public URL: `https://phc.alshifalab.pk`
- Internal app port: `127.0.0.1:8018`
- App container port: `8000`

This is a fresh app from scratch. Do not continue, repair, copy, or merge the old AccrediOps architecture.

---

## Primary Objective

Build a small, practical, single-purpose Django monolith for one fixed Punjab Healthcare Commission MSDS Clinical/Pathology Laboratory checklist.

The application must answer one question:

> Are we ready for PHC Lab inspection, and where is the evidence?

The checklist is fixed:

- 37 standards
- 118 indicators
- PHC scoring logic
- evidence readiness tracking
- digital registers
- recurring compliance tracking
- printable surveyor-ready packs

---

## Absolute Scope Boundaries

Do not build:

- generic accreditation platform
- multi-framework builder
- project/workspace abstraction
- CAPA board
- complex RBAC
- Next.js frontend
- React frontend
- live AI dependency
- multi-tenant SaaS logic
- old AccrediOps compatibility layer
- unnecessary analytics or decorative dashboards

Build only what directly supports PHC Lab inspection readiness.

---

## Required Technical Stack

Use:

- Django monolith
- Django templates
- HTMX only where useful
- PostgreSQL
- Bootstrap or simple Tailwind
- Django admin
- Docker Compose
- Gunicorn
- WeasyPrint or ReportLab for PDF exports
- Caddy reverse proxy

Preferred Django apps:

- `core`
- `accounts`
- `indicators`
- `evidence`
- `registers`
- `reports`

---

## Session Continuity Requirement

Before implementation, create or overwrite:

```text
copilot_session.md
```

Keep it updated throughout the session.

It must include:

- project objective
- scope boundaries
- repository state
- source files found
- implementation plan
- task checklist
- data mapping decisions
- completed work
- pending work
- tests run
- test results
- deployment notes
- limitations
- handoff notes

The purpose is to allow another agent to continue without redoing work.

---

## Source File Rules

The folder:

```text
data/seed/
```

may be empty. Do not depend on seed files.

The real source files should be in:

```text
data/source_materials/
```

Expected source files may include:

```text
test-export_framework_template_FIXED.csv
SM MSDS Pathology-CLs-2505-QA2605-Rev100718.pdf
4thC-RevAnnexs-MSDS  RM Clinical Labs-220518-240518.docx
```

The CSV is the primary operational source.

Rules:

- If the real CSV exists, inspect and import it.
- If the CSV column names differ, map them sensibly and document the mapping.
- Do not fake 118 indicators.
- Do not treat a sample/template as complete data.
- If import is incomplete, clearly mark it as partial or blocked.

---

## Core Data Model Requirements

### Indicator

Locked PHC master checklist record.

Required fields:

- `indicator_no`
- `functional_area_code`
- `functional_area_name`
- `standard_no`
- `standard_code`
- `standard_title`
- `indicator_text`
- `max_score`
- `weightage_percent`
- `compliance_requirement`
- `surveyor_check`
- `required_evidence`
- `evidence_category`
- `register_required`
- `register_name`
- `recurring_required`
- `recurrence_frequency`
- `document_to_generate`
- `physical_action_required`
- `is_locked`
- `source_reference`
- `created_at`
- `updated_at`

Rules:

- `indicator_no` must be unique.
- Real import should result in exactly 118 indicators.
- Master indicator text should be locked from normal UI editing.
- Admin may edit locked records only if required.

### IndicatorCompliance

Working state for each indicator.

Required fields:

- `indicator`
- `evidence_status`
- `current_score`
- `gap_summary`
- `next_action`
- `evidence_location`
- `ready_for_print_pack`
- `notes`
- `updated_by`
- `updated_at`

Evidence status values:

- `missing`
- `partial`
- `ready`
- `verified`
- `not_applicable`

Simple scoring rule:

- missing = 0
- partial = 80% of max score where partial compliance is acceptable
- ready = max score
- verified = max score
- not applicable = handled explicitly and documented

Do not overcomplicate scoring in the MVP.

---

## Required Management Command

Create:

```bash
python manage.py import_phc_indicators data/source_materials/test-export_framework_template_FIXED.csv
```

Command name:

```text
import_phc_indicators
```

Requirements:

- read CSV from path argument
- map available CSV columns to Indicator fields
- clean whitespace
- preserve PHC wording
- create or update by indicator number
- create missing IndicatorCompliance rows
- validate unique indicator numbers
- validate total count
- print count and functional area summary
- report missing indicator numbers if count is not 118
- document import result in `copilot_session.md`

---

## Required UI

Keep UI simple and server-rendered.

Navigation:

- Dashboard
- Indicators
- Evidence
- Registers
- Reports
- Admin

### Indicator list

Must support:

- all 118 indicators
- search
- filter by functional area
- filter by evidence status
- filter by evidence category
- register required yes/no
- recurring required yes/no
- score/status display

### Indicator detail

Must show:

- standard
- indicator text
- score/weightage
- compliance requirement
- surveyor check
- required evidence
- linked evidence
- linked registers
- gap summary
- next action
- evidence status update form
- ready for print pack checkbox

---

## Evidence Library

Implement evidence types:

- SOP / Policy
- Register / Logbook
- Recurring Record
- Physical Display / Photo
- Certificate / License / MOU
- Staff File / HR Record
- Patient Record / Reporting System
- Audit / QA Report
- Other

Evidence features:

- upload file
- add external URL/path
- link one evidence item to multiple indicators
- show evidence on indicator detail
- filter evidence by type and indicator

---

## Digital Registers

Registers must be maintained digitally and printable on demand.

Implement:

- `RegisterDefinition`
- `RegisterEntry`

Initial register definitions:

1. Temperature Log
2. Equipment Logbook
3. Equipment Maintenance Register
4. Calibration Register
5. Reagent Inventory
6. Stock Register
7. EQA Record
8. IQA / Process Cycle Record
9. Complaint Register
10. Critical Result Register
11. Fire Drill Register
12. Training Register
13. Waste Disposal Register
14. Incident / Sentinel Event Register

Each register definition should link to relevant PHC indicators.

Use flexible JSON fields initially, but keep the UI practical.

---

## Recurring Compliance

Support frequencies:

- Daily
- Weekly
- Monthly
- Quarterly
- Annual
- Event-based
- One-time

For recurring registers:

- calculate last entry
- calculate next due
- detect overdue
- detect due soon
- show overdue/due soon on dashboard
- generate recurring compliance report

Default due-soon window: 7 days.

Event-based registers should not automatically become overdue unless manually flagged.

---

## Dashboard Requirements

Dashboard cards:

- total indicators
- missing indicators
- partial indicators
- ready indicators
- verified indicators
- current score
- maximum score
- readiness percentage
- evidence items
- active registers
- overdue registers
- due soon registers

Dashboard tables:

- functional area summary
- standard-wise progress
- missing evidence list
- overdue recurring registers
- recently updated indicators

No unnecessary charts.

---

## Reports and Print Pack

Implement print-friendly pages and PDF export where feasible:

- PHC score summary
- indicator-wise compliance report
- standard-wise evidence index
- missing evidence report
- recurring compliance report
- register printouts
- surveyor pack index
- final surveyor pack placeholder/export

If PDF export is hard, implement print-friendly HTML first and document limitation.

---

## Docker and Deployment

Expected Docker behavior:

```bash
docker compose up -d --build
```

Web service should:

- run migrations
- collectstatic
- start Gunicorn
- bind container port 8000
- map host `127.0.0.1:8018` to container `8000`

Required health check:

```bash
curl -I http://127.0.0.1:8018/health/
```

Caddy block:

```caddy
phc.alshifalab.pk {
    encode zstd gzip
    reverse_proxy 127.0.0.1:8018
}
```

Possible Caddyfile path:

```text
/home/munaim/srv/proxy/caddy/Caddyfile
```

Document both Docker Caddy reload and system Caddy reload options. Do not modify unrelated Caddy blocks.

---

## Quality Gates

Run as many as possible:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
pytest
ruff check .
docker compose build
docker compose up -d
docker compose ps
curl -I http://127.0.0.1:8018/health/
```

If a check fails, fix it if reasonable. If not fixable in this sprint, document the exact failure and reason.

---

## Documentation Requirements

Create or update:

```text
README.md
docs/00_project/APP_DESCRIPTION.md
docs/00_project/GOALS.md
docs/10_architecture/ARCHITECTURE.md
docs/20_data_model/DATA_MODEL.md
docs/30_tests/TESTS.md
docs/40_operations/SETUP.md
docs/40_operations/DEPLOYMENT_CADDY.md
docs/90_handoff/FINAL_IMPLEMENTATION_SUMMARY.md
copilot_session.md
```

Documentation must include:

- how to run locally
- how to import indicators
- how to create admin user
- how to run tests
- how to deploy with Docker
- how to configure Caddy
- current limitations

---

## Git Rule

If git is initialized:

```bash
git status
git add .
git commit -m "Initial PHC Lab Compliance Tracker MVP"
```

If git is not initialized, do not force it unless appropriate. Document the status.

---

## Final Response Format

End with:

```text
Final verdict: GO / PARTIAL GO / BLOCKED

What works:
- ...

Source files used:
- ...

Indicator import status:
- ...

Tests run:
- ...

What remains:
- ...

How to run:
- ...

How to import indicators:
- ...

How to deploy to phc.alshifalab.pk:
- ...

Important notes:
- ...
```
