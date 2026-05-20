# Final AI Developer Prompt

You are working on the PHC Lab Compliance Tracker project.

Before doing any coding, create or overwrite a root-level file named `copilot_session.md`. In that file, document your understanding of the prompt, repository state, complete execution plan, task checklist, expected file changes, tests, risks, and progress updates.

Keep `copilot_session.md` actively updated so another agent can continue without redoing analysis.

## Project Goal

Build a single-purpose Django monolith called PHC Lab Compliance Tracker for Al Shifa Laboratory. The app tracks PHC/MSDS Clinical / Pathology Laboratory inspection readiness for one fixed checklist: 37 standards and 118 indicators.

No multi-framework abstraction. No SaaS. No live AI API.

Core question: Are we ready for PHC Lab inspection, and where is the evidence?

## Key Architecture Rule

Do not link evidence only directly to indicators.

Implement this structure:

```text
Indicator
  → EvidenceRequirement
      → EvidenceItem / RegisterEntry
```

One indicator may require multiple evidence items.

## Required Django Apps

```text
core
accounts
indicators
evidence
registers
reports
```

## Core Models

Implement:
1. Indicator
2. EvidenceRequirement
3. EvidenceItem
4. EvidenceRequirementFulfillment
5. RegisterDefinition
6. RegisterEntry

## Required Features

- Authentication and health endpoint.
- Import 118 indicators from CSV.
- Bootstrap evidence requirements.
- Evidence library with uploads, URLs, and physical references.
- Evidence requirement fulfillment.
- Digital registers and entries.
- Register entries can act as evidence.
- Dashboard with readiness score.
- Missing evidence report at requirement level.
- Surveyor pack index.
- Prompt-only AI generator per evidence requirement.

## Status Logic

Evidence requirement statuses:

```text
MISSING
DRAFT
PENDING_REVIEW
PARTIAL
READY
VERIFIED
REJECTED
EXPIRED
NOT_APPLICABLE
```

Indicator status is calculated from evidence requirement statuses.

## Scoring Logic

Missing = 0. Partial = partial score only if PHC allows partial compliance. Ready = full score. Verified = full score. Not applicable = excluded only with documented approval.

## URLs

```text
/                              Dashboard
/health/                       Health
/accounts/login/               Login
/accounts/logout/              Logout
/indicators/                   Indicator list
/indicators/<id>/              Indicator detail
/evidence/                     Evidence list
/evidence/add/                 Add evidence
/evidence/<id>/                Evidence detail
/registers/                    Register list
/registers/<id>/               Register detail
/registers/<id>/entries/add/   Add register entry
/registers/<id>/print/         Print register
/reports/                      Reports home
/reports/score-summary/        Score summary
/reports/missing-evidence/     Missing evidence
/reports/evidence-index/       Evidence index
/reports/recurring/            Recurring report
/reports/surveyor-pack/        Surveyor pack
/admin/                        Django admin
```

## Quality Gates

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
pytest
ruff check .
docker compose build
docker compose up -d
curl -I http://127.0.0.1:8018/health/
```

## Do Not Add

Do not add multi-framework architecture, project/workspace abstraction, CAPA board, live AI API, complex RBAC, React/Next.js frontend, billing/SaaS features, or advanced charts.
