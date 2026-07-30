# Backend (Django + DRF)

Not yet a real Django project — this is a placeholder layout for Stage 0 to
fill in properly (`django-admin startproject`, `startapp`, etc.). Don't
hand-write `manage.py`/`settings.py`/migrations; let the framework generate
them so they're correct.

## Intended app boundaries

- `apps/registry/` — Stage 0. Domain, Standard, Indicator, LabProfile models.
  Read-only registry view + filters.
- `apps/evidence/` — Stage 1. EvidenceRecord model, daily due-list logic
  (presence-only, no deadline/lateness — see decision #7).
- `apps/compliance/` — Stage 1/2. Compliance % computation (earned weightage
  ÷ possible weightage across all 118 — see `AI_DEV_PACK.md` §2).
- `apps/exports/` — Stage 2. Print/export engine, ordered per decision #8.
- `apps/drafting/` — Section B. Draft model (document|template), generation
  via the Anthropic API, human review/approval workflow (decision #13).

## requirements.txt (starting point — adjust as Stage 0 proceeds)

```
django>=5.0
djangorestframework
psycopg2-binary
django-cors-headers
celery
redis
gunicorn
python-dotenv
anthropic
```
