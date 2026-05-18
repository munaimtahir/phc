# AGENTS.md

## Purpose

This file guides AI coding agents working on the `phc` repository.

The goal is to build a small, reliable, single-purpose PHC Lab Compliance Tracker. Agents must avoid drifting into a large generic accreditation platform.

---

## Operating Principle

The app exists to help a laboratory prepare for PHC/MSDS Clinical/Pathology Laboratory inspection.

Every implementation decision should serve one of these outcomes:

1. Show the fixed PHC Lab checklist.
2. Track evidence readiness.
3. Maintain required registers digitally.
4. Track recurring compliance records.
5. Calculate PHC readiness score.
6. Print a surveyor-ready evidence pack.

If a feature does not support these outcomes, do not build it in the MVP.

---

## Project Boundaries

### Build

- Django monolith
- server-rendered templates
- simple navigation
- locked 118-indicator checklist
- evidence library
- digital registers
- recurring due/overdue tracking
- reports and printable views
- Docker deployment
- Caddy deployment documentation

### Do Not Build

- generic accreditation system
- multi-framework platform
- CAPA board
- Next.js/React frontend
- complex RBAC
- live AI-based workflow
- multi-tenant SaaS
- project/workspace abstraction
- old AccrediOps compatibility
- decorative analytics

---

## Required Agent Workflow

### 1. Start by updating session file

Create or overwrite:

```text
copilot_session.md
```

Keep it updated continuously.

At minimum include:

- repository state
- source files found
- planned tasks
- completed tasks
- pending tasks
- commands run
- test results
- deployment notes
- handoff notes

### 2. Inspect before coding

Check:

```bash
pwd
find . -maxdepth 3 -type f | sort
ls -la
ls -la data/source_materials || true
ls -la data/seed || true
git status || true
```

Document findings.

### 3. Prefer simple implementation

Use Django built-ins before custom complexity.

Prefer:

- Django admin over custom settings screens
- class/function-based views over heavy frontend state
- print-friendly HTML before advanced PDF styling
- JSON schema fields for flexible register entries in MVP
- simple permissions: authenticated/staff access

### 4. Keep data honest

Do not invent complete data.

If real CSV import does not produce 118 indicators, mark it clearly.

### 5. Test before final response

Run available quality gates and document exact results.

---

## Suggested Agent Roles

A single agent may perform all roles. If subagents are available, divide work as follows.

### Repository Auditor

Responsibilities:

- inspect repository tree
- identify source materials
- inspect CSV columns
- detect missing files
- update `copilot_session.md`

Outputs:

- repository status
- source file status
- data mapping notes

### Backend Builder

Responsibilities:

- create Django apps
- implement models
- implement import command
- implement score logic
- configure settings/database/static/media
- implement admin

Outputs:

- migrations
- management commands
- model tests

### UI Builder

Responsibilities:

- base template/sidebar
- dashboard
- indicator list/detail
- evidence pages
- register pages
- report pages

Outputs:

- templates
- forms
- URL routes
- protected views

### Evidence/Register Builder

Responsibilities:

- evidence model/forms/views
- register definition/entry model
- recurrence logic
- printable register pages

Outputs:

- evidence library
- digital register module
- recurring due/overdue logic

### Reports Builder

Responsibilities:

- score summary
- evidence index
- missing evidence report
- recurring compliance report
- surveyor pack index
- PDF or print-friendly HTML

Outputs:

- report routes
- templates
- PDF utility if feasible

### QA/Deployment Agent

Responsibilities:

- tests
- `manage.py check`
- migration check
- lint
- Docker build
- health check
- Caddy documentation

Outputs:

- test report
- deployment instructions
- final summary

---

## Data Source Handling

Expected real source folder:

```text
data/source_materials/
```

Expected files:

```text
test-export_framework_template_FIXED.csv
SM MSDS Pathology-CLs-2505-QA2605-Rev100718.pdf
4thC-RevAnnexs-MSDS  RM Clinical Labs-220518-240518.docx
```

The operational source is the CSV.

The PDF/DOCX are supporting references.

The folder:

```text
data/seed/
```

may be empty. Do not fail because it is empty.

---

## Import Command Contract

Create:

```bash
python manage.py import_phc_indicators data/source_materials/test-export_framework_template_FIXED.csv
```

The command must:

- accept a CSV path
- inspect columns
- map available fields
- import/update by indicator number
- create compliance rows
- detect duplicates
- detect missing indicator numbers
- report final count
- warn if count is not 118

Do not silently pass incomplete imports.

---

## Model Contract

### Indicator

Locked source-of-truth requirement.

Must include:

- indicator number
- functional area
- standard
- indicator text
- score/weightage
- evidence category
- register requirement
- recurring requirement
- guidance fields
- locked flag

### IndicatorCompliance

Working state.

Must include:

- status
- score
- gap
- next action
- evidence location
- print readiness
- notes
- update user/time

### EvidenceItem

Evidence file/link.

Must include:

- title
- evidence type
- file or URL/path
- linked indicators
- description
- date
- uploader

### RegisterDefinition

Digital register template.

Must include:

- name
- category
- frequency
- fields schema
- linked indicators
- printable flag

### RegisterEntry

Single register entry.

Must include:

- register definition
- entry date
- values JSON
- entered by
- verification fields
- remarks

---

## UI Contract

Minimum pages:

```text
/
 /health/
 /accounts/login/
 /accounts/logout/
 /indicators/
 /indicators/<id>/
 /evidence/
 /evidence/<id>/
 /registers/
 /registers/<id>/
 /reports/
 /reports/score-summary/
 /reports/missing-evidence/
 /reports/evidence-index/
 /reports/recurring/
 /admin/
```

All operational pages should require login unless deliberately public.

---

## Register Templates

Create initial register definitions:

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

Each register should be printable.

---

## Recurrence Rules

Supported frequency values:

- Daily
- Weekly
- Monthly
- Quarterly
- Annual
- Event-based
- One-time

Due logic:

- Daily: next day after last entry
- Weekly: 7 days after last entry
- Monthly: 1 month after last entry
- Quarterly: 3 months after last entry
- Annual: 1 year after last entry
- One-time: no recurring due date after first entry
- Event-based: no automatic overdue unless manually flagged

Due soon default: next 7 days.

---

## Report Contract

Reports must be simple and useful.

Required:

- score summary
- indicator compliance report
- evidence index
- missing evidence report
- recurring compliance report
- register printouts
- surveyor pack index

Use print-friendly HTML first. Add PDF export if feasible.

---

## Deployment Contract

The app should be deployable with:

```bash
docker compose up -d --build
```

Expected local health check:

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

Document reload according to detected setup.

---

## Quality Gate Commands

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

If any command is not runnable due to environment limits, document why.

---

## Documentation Contract

Create/update:

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

---

## Commit Contract

If git is initialized and work is complete enough:

```bash
git status
git add .
git commit -m "Initial PHC Lab Compliance Tracker MVP"
```

If git is not initialized, do not force it unless appropriate. Document status.

---

## Final Agent Response Contract

Finish with:

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

---

## Important Reminder

Keep the app boring, practical, and inspection-ready.

A complete simple tracker is better than an incomplete advanced platform.
