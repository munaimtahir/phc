# Final AI Developer Prompt

You are working in a fresh repository named `phc`.

This is a new app from scratch. Do not continue the old AccrediOps architecture. Treat the old project only as background/historical reference.

## Session continuity requirement

Create or overwrite a root-level file named `copilot_session.md`.

After reviewing this prompt and the repository, document in `copilot_session.md`:
- project objective,
- scope boundaries,
- complete execution plan,
- task checklist,
- decisions made,
- completed work,
- pending work,
- test results,
- deployment notes,
- handoff notes.

Keep `copilot_session.md` actively updated throughout the session so another agent can continue without redoing work if this session ends.

## Project identity

App/repo/folder name: `phc`  
Product name: PHC Lab Compliance Tracker  
Server path: `/home/munaim/srv/apps/phc`  
Public URL: `https://phc.alshifalab.pk`

## Main objective

Build a single-purpose Django monolith for one fixed Punjab Healthcare Commission MSDS Clinical/Pathology Laboratory checklist.

The checklist is fixed:
- 37 standards
- 118 indicators
- PHC scoring matrix logic
- evidence readiness
- digital registers
- recurring compliance records
- printable surveyor-ready pack

The app must answer one question:

> Are we ready for PHC Lab inspection, and where is the evidence?

## Hard scope boundaries

Do not build:
- generic accreditation platform
- multi-framework builder
- framework import/export UI for normal users
- CAPA board
- complex RBAC
- Next.js frontend
- live AI dependency
- multi-tenant SaaS logic
- project/workspace abstraction

Use:
- Django
- Django templates
- HTMX where useful
- PostgreSQL
- Bootstrap or simple Tailwind
- WeasyPrint or ReportLab for PDFs
- Docker Compose
- Caddy reverse proxy

## Deployment requirement

The app must run behind Caddy at:

```text
https://phc.alshifalab.pk
```

Use internal app port mapping:

```text
127.0.0.1:8018 -> container web:8000
```

Add this Caddy block to the deployment documentation and, if appropriate, provide a script/snippet file:

```caddy
phc.alshifalab.pk {
    encode zstd gzip
    reverse_proxy 127.0.0.1:8018
}
```

Assume Caddyfile location may be:

```text
/home/munaim/srv/proxy/caddy/Caddyfile
```

Also mention that the deployed Caddyfile may need to be synced/reloaded depending on the existing server setup.

## Build maximum combined phases in one sprint

Implement as much as possible in one coordinated sprint, but keep the code simple and verifiable.

### Phase 1 — Foundation
- Create Django project structure.
- Create apps:
  - core
  - accounts
  - indicators
  - evidence
  - registers
  - reports
- Configure PostgreSQL via `DATABASE_URL`.
- Configure static/media.
- Add login/logout and simple staff-only access.
- Add a health endpoint.
- Add Dockerfile and docker-compose.
- Add basic responsive base layout/sidebar.

### Phase 2 — Locked PHC indicator register
- Implement `Indicator` model.
- Implement `IndicatorCompliance` model.
- Add CSV import/seed command for locked PHC indicator master list.
- Enforce exactly 118 indicators after import.
- Enforce unique indicator numbers.
- Prevent normal UI editing of locked master indicator text.
- Allow working fields to be edited:
  - evidence status
  - current score
  - gap summary
  - next action
  - evidence location/link
  - notes
  - ready for print pack

### Phase 3 — Evidence library
- Implement evidence categories:
  - SOP / Policy
  - Register / Logbook
  - Recurring Record
  - Physical Display / Photo
  - Certificate / License / MOU
  - Staff File / HR Record
  - Patient Record / Reporting System
  - Audit / QA Report
- Implement evidence upload/link form.
- Allow one evidence item to link to multiple indicators.
- Show evidence linked to each indicator.
- Add evidence list filters by category and indicator.

### Phase 4 — Digital registers
- Implement `RegisterDefinition`.
- Implement `RegisterEntry`.
- Registers must be digitally maintained and printable on demand.
- Register definitions should link to one or more PHC indicators.
- Add initial register templates:
  - Temperature Log
  - Equipment Logbook
  - Equipment Maintenance Register
  - Calibration Register
  - Reagent Inventory
  - Stock Register
  - EQA Record
  - IQA / Process Cycle Record
  - Complaint Register
  - Critical Result Register
  - Fire Drill Register
  - Training Register
  - Waste Disposal Register
  - Incident / Sentinel Event Register
- Use flexible JSON fields for register entries at first, but present clean forms where feasible.

### Phase 5 — Recurring compliance
- Add recurrence frequency:
  - Daily
  - Weekly
  - Monthly
  - Quarterly
  - Annual
  - Event-based
  - One-time
- Add last entry and next due calculation for recurring registers.
- Dashboard must show due and overdue register items.
- Register pages must show printable monthly/periodic views.

### Phase 6 — Dashboard
Dashboard should show:
- total indicators
- ready indicators
- partial indicators
- missing indicators
- verified indicators
- current score
- maximum score
- readiness percentage
- overdue recurring registers
- due-soon recurring registers
- missing high-priority evidence
- standard-wise summary

### Phase 7 — Reports and surveyor pack
Implement printable/exportable reports:
- PHC score summary
- indicator-wise compliance report
- standard-wise evidence index
- missing evidence report
- recurring compliance report
- register printouts
- final surveyor pack placeholder page

PDF output may be basic at first, but must be functional.

### Phase 8 — Tests and quality gates
Add tests for:
- seed/import creates exactly 118 indicators
- indicator numbers are unique
- dashboard loads
- indicator list/detail loads
- compliance status update works
- score calculation works
- evidence item can link to indicators
- register definition and entry creation works
- recurring due/overdue logic works
- report pages return 200
- health endpoint returns 200

Run:
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

## Data/import requirement

Use `data/seed/phc_indicators_master_template.csv` as a temporary template only.

The real source should be the finalized PHC 118-indicator CSV placed in:

```text
data/source_materials/
```

Create the import command so it can import from:

```bash
python manage.py import_phc_indicators data/source_materials/<final-csv-file>.csv
```

If the final CSV is not present, create the model/import command and seed a small sample safely without pretending all 118 indicators exist.

## UI requirement

Keep UI simple:
- Dashboard
- Indicators
- Evidence
- Registers
- Reports
- Settings/Admin

No fancy animations. No complex enterprise UI. Prioritize fast data entry and clear printing.

## Final deliverables

At the end, produce:
1. Updated `copilot_session.md`
2. Working Django app
3. Docker Compose deployment
4. Caddy block documented
5. Import command
6. Evidence/register models and screens
7. Dashboard
8. Reports
9. Tests
10. Final summary in:

```text
docs/90_handoff/FINAL_IMPLEMENTATION_SUMMARY.md
```

## Final verdict format

End with:

```text
Final verdict: GO / PARTIAL GO / BLOCKED

What works:
- ...

What remains:
- ...

How to run:
- ...

How to deploy to phc.alshifalab.pk:
- ...
```
