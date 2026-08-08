# Agent Handoff — PHC MSDS Compliance Tracker

Written: 2026-08-03, end of the build session that took this repo from
pre-code scaffold to all four stages built, quality-gated, and running live
in Docker Compose. Munaim will come back and ask an agent to **verify the
build and application readiness** — that agent should read this document
first, it has full context of what's done, what's left, and exactly how to
finish. Update this file as you go; don't let it go stale the way
`docs/status/DEVELOPMENT_STATUS.md` almost did.

## TL;DR for the next agent

1. Everything in `BUILD_PROMPT.md` (Stage 0, Stage 1, Stage 2, Section B) is
   built and passes its automated Quality Gate — **34/34 backend tests green**.
   Frontend builds clean, 4 pages implemented.
2. The full stack is **already running** in Docker Compose
   (project name `phc-msds-tracker`) and has been live smoke-tested for
   everything except one thing.
3. **The one blocking item:** Section B's real Anthropic API generation has
   never been exercised against a real API key — `.env` still has
   `ANTHROPIC_API_KEY=changeme`. Get a real key from Munaim, drop it in
   `.env`, restart the backend container, and run the exact commands in
   [Finish the Section B smoke test](#finish-the-section-b-smoke-test) below.
4. There's a leftover **fake placeholder draft** (Draft id=1, indicator #9)
   created during this session to demonstrate the approve/reject mechanism
   without a real API key. Delete it before calling the pilot done — see
   [Cleanup](#cleanup-before-final-verification).
5. Do **not** touch `/etc/caddy/Caddyfile` or anything under
   `/home/munaim/srv/proxy/` without explicit confirmation from Munaim first
   — this host runs a shared production Caddy instance serving other live
   apps (see [Public exposure](#public-exposure-via-caddy---needs-explicit-go-ahead)).

---

## What was built (all four stages, in one session)

### Stage 0 — Registry + Lab Profile
- Real Django project scaffolded at `backend/` (`django-admin startproject`,
  `startapp` — not hand-written) with apps `apps/registry`, `apps/evidence`,
  `apps/compliance`, `apps/exports`, `apps/drafting`.
- Models: `Domain`, `Standard`, `Indicator`, `LabProfile` in
  `backend/apps/registry/models.py`.
- Loader: `backend/apps/registry/management/commands/load_indicators.py` reads
  `docs/data/indicators_master.json` (untouched, canonical) and transforms it
  into the DB — `compliance_requirements`/`survey_process`/`scoring`/
  `guidelines` are stored as `JSONField` (list), preserving the source
  structure exactly for byte-for-byte spot checks.
- `retention_months` isn't in the source JSON — set in the loader per
  `AI_DEV_PACK.md` decision #3: `recurring` → 12 months, `physical`/`one_time`
  → `null`. This is a **decided rule**, not invented — just not literally a
  JSON field.
- Read-only filterable DRF views at `/api/registry/` (domains, standards,
  indicators with `?domain=`/`?category=`/`?frequency=`/`?evidence_format=`
  filters) + `/api/registry/lab-profile/`.
- **Quality Gate: 11/11 tests pass** —
  `backend/apps/registry/tests/test_stage0_quality_gate.py`. Covers exact
  118/37/10 counts, per-domain counts, weightage/category/evidence_format
  splits, byte-for-byte spot check against source JSON, LabProfile seed
  values, and the two named filter checks (`domain=ROM` → 13,
  `category=recurring` → 57).

### Stage 1 — Recurring entry + due-list + compliance scoring
- `EvidenceRecord` model in `backend/apps/evidence/models.py`.
- `backend/apps/evidence/services.py`:
  - `current_period_label()` — the exact period-label formats from
    `AI_DEV_PACK.md` (daily `YYYY-MM-DD`, weekly `YYYY-Www`, monthly `YYYY-MM`,
    quarterly `YYYY-Qn`, biannual `YYYY-H1`/`H2`, annual `YYYY`, `as_needed` →
    `None`).
  - `due_list()` — presence-only check for recurring non-`as_needed`
    indicators, no lateness logic (decision #7).
  - `submit_evidence()` — handles the physical/one-time "exactly one
    `is_current=true`, replaced not accumulated" rule vs. recurring's
    "one record per period, `update_or_create` on `(indicator, period_label)`"
    vs. `as_needed`'s "always a new record, never period-keyed, never on the
    due-list."
  - `prune_expired_evidence()` — the retention job; only prunes recurring
    records past `retention_months`, never touches physical/one-time current
    records.
- Structured-form field schemas: `backend/apps/evidence/structured_forms.py`
  — see [Parked Decision #1](#parked-decision-1-structured_form-field-sets)
  below, this is the one open decision gap.
- Compliance scoring: `backend/apps/compliance/services.py` —
  `indicator_snapshot()` uses each indicator's **most recent** `EvidenceRecord`
  (by `submitted_at`, not necessarily the current period's), 3-tier
  fully_met/partially_met(only if `allows_partial`)/not_met scoring, and
  `compliance_snapshot()` sums earned/possible weightage across all 118 live.
- API: `/api/evidence/due-list/`, `/api/evidence/submit/`,
  `/api/evidence/structured-form-schema/<id>/`,
  `/api/evidence/history/<id>/`, `/api/compliance/`.
- **Quality Gate: 10/10 tests pass** —
  `backend/apps/evidence/tests/test_stage1_quality_gate.py`. Covers the
  hand-built due-list fixture, physical/one-time and `as_needed` exclusion
  from the due-list, `partially_met` rejection when `allows_partial=False`,
  no-null-period-label invariant, retention pruning (old recurring record
  pruned, current one-time record never pruned), the hand-calculated
  compliance fixture across 10+ indicators/all three statuses, "most recent
  not current period" behavior, and an API-level test hitting `/submit/` with
  all three `evidence_format` types.

### Stage 2 — Print/export engine
- `backend/apps/exports/services.py::generate_print_pack_pdf()` — reportlab,
  ordered by `Indicator.objects.order_by("id")` (which **is** the
  domain→standard→indicator sequence, confirmed against
  `indicators_master.json`). Every indicator appears exactly once, indicators
  with no evidence are explicitly marked "No evidence submitted.", overall
  compliance % is computed live at generation time via
  `compliance.services.compliance_snapshot()` (not cached).
- API: `/api/exports/print-pack/` (GET, returns the PDF).
- **Quality Gate: 5/5 tests pass** —
  `backend/apps/exports/tests/test_stage2_quality_gate.py`, using `pypdf` to
  extract and assert on the actual rendered text (not just "PDF didn't
  crash"). Covers exactly 118 entries no dupes, order matches source ID
  sequence, no-evidence indicators still appear marked, and — importantly —
  regenerating after submitting new evidence changes the displayed % (proves
  it's live, not cached).

### Section B — AI Drafting Assistant
- `Draft` model in `backend/apps/drafting/models.py`
  (`kind=document|template`, `status=draft|approved|rejected`).
- `backend/apps/drafting/services.py`:
  - `draft_kind_for_indicator()` — `one_time` → `document`,
    `recurring` + `evidence_format in {document, structured_form}` →
    `template`, everything else (including all `physical`) → not eligible.
  - `generate_draft()` — calls the real Anthropic API
    (`client.messages.create(model="claude-sonnet-5", ...)`), grounds the
    prompt in the indicator's `compliance_requirements` + `survey_process` +
    `LabProfile` fields (so drafts name Al Shifa Laboratory / Circular Road,
    Jaranwala / P-20787 / Dr. Mubashr Ahmed directly, per decision #10/#13).
  - `bulk_generate_drafts()` — only targets `eligible_indicators()` that lack
    current evidence (`is_current=True` EvidenceRecord for `document`
    indicators; no approved `template` Draft yet for `template` indicators).
    Indicators that already have current evidence are skipped, not
    overwritten.
  - `approve_draft()` — **requires non-empty `reviewed_by`**, raises
    `ValidationError` otherwise. For `document` drafts, calls
    `evidence.services.submit_evidence()` to create a new `is_current=True`
    `EvidenceRecord` (status `fully_met`, `structured_data` carries
    `{source: "ai_draft", draft_id, content}`), superseding (not deleting)
    the previous current record. For `template` drafts, **touches no
    `EvidenceRecord` at all** — just flips the Draft's own status.
  - `reject_draft()` — same `reviewed_by` requirement, no evidence side
    effects either way.
- API: DRF router at `/api/drafting/drafts/` (list/retrieve, filterable by
  `status`/`kind`/`indicator`) plus custom actions:
  `eligible_indicators_list/`, `generate/`, `bulk_generate/`,
  `<id>/approve/`, `<id>/reject/`, and `/api/drafting/template/<indicator_id>/`
  (retrieves the latest approved template for an indicator).
- Anthropic API errors (bad/missing key, etc.) are caught and returned as a
  clean `502` with the underlying message — not a raw Django debug page. See
  `backend/apps/drafting/views.py`.
- **Quality Gate: 8/8 tests pass** —
  `backend/apps/drafting/tests/test_section_b_quality_gate.py`, Anthropic
  client mocked. This includes the single most load-bearing test in the whole
  build: **`test_draft_and_rejected_drafts_never_readable_from_evidence_or_print_path`**
  — proves a `draft`/`rejected` Draft never creates an `EvidenceRecord` and
  never appears in the print pack text. Also covers: approving a `document`
  draft supersedes-not-deletes the prior current record; approving a
  `template` draft never touches `EvidenceRecord`; approve without
  `reviewed_by` is rejected; approved records always have non-null
  `reviewed_by`/`reviewed_at`; bulk generation skips indicators with current
  evidence and only targets the eligible scope (never `physical`); a draft
  never appears in the print export until approved.

### Frontend
- Real Vite project (`npm create vite@latest . -- --template react-ts`) with
  Tailwind v4 (`@tailwindcss/vite` plugin, `@import "tailwindcss"` in
  `src/index.css` — note someone/something already tweaked the font-family in
  there post-scaffold, left as-is).
- `react-router-dom` for routing, `src/lib/api.ts` is the single fetch
  wrapper + API base URL (`VITE_API_BASE_URL` env var).
- **Auth: HTTP Basic**, not session/cookie — deliberate simplification for
  the single-shared-login MVP (decision #4). `src/lib/auth.ts` stores
  base64(user:pass) in `sessionStorage` and every `api.*` call sends it as an
  `Authorization: Basic ...` header. This sidesteps Django CSRF entirely
  (DRF's `APIView` is CSRF-exempt at the Django level; `SessionAuthentication`
  is the only thing that re-imposes a CSRF check, and the frontend never uses
  session auth). `config/urls.py::login_view` just validates credentials via
  `django.contrib.auth.authenticate()` — there's no server-side session to
  start.
- Pages: `src/pages/registry/RegistryPage.tsx` (filterable table + overall
  compliance banner), `src/pages/daily/DailyPage.tsx` (due-list + inline
  entry form that renders the right input per `evidence_format` — file
  upload for photo/document, dynamic fields from
  `/structured-form-schema/<id>/` for structured_form), `src/pages/print/PrintPage.tsx`
  (triggers `/exports/print-pack/` and downloads the blob),
  `src/pages/drafting/DraftingPage.tsx` (generate/bulk-generate + review
  queue with approve/reject, `reviewed_by` prompted from the logged-in
  username or a text prompt).
- `npx tsc -b` and `npm run build` both clean, no errors.

---

## Locked decisions this build relied on (for context, not re-litigation)

All from `docs/decisions/0001-locked-decisions.md` and `AI_DEV_PACK.md` — see
those files for full reasoning. Not re-decided here, just listed so the next
agent doesn't second-guess them:

- Single shared login, 2-3 staff (#4) → implemented as HTTP Basic with one
  seeded Django user (see [Credentials](#credentials--how-to-reach-it)).
- Recurring evidence retention ~12 months, physical/one-time keep only
  current (#3) → `retention_months` set in the loader, not the source JSON.
- Due-list is presence-only, no lateness (#7).
- Print pack ordering mirrors PHC's own domain→standard→indicator numbering
  (#8) → this is just `Indicator.objects.order_by("id")`.
- Section B: document drafts for one-time, template drafts for recurring
  *documentary* indicators (`evidence_format` document/structured_form),
  never physical (#11); on-demand + bulk generation (#12); draft→human
  approval required, never automatic (#13, and the non-negotiable rule at
  the top of `BUILD_PROMPT.md`).

---

## Parked Decision #1 — structured_form field sets

Full writeup already in `docs/status/PARKED_DECISIONS.md`. Short version:
indicators #6, #44, #46, #50 (structured_form) don't have an explicit field
list in their `compliance_requirements` text the way #53 does, so
`backend/apps/evidence/structured_forms.py::STRUCTURED_FORM_SCHEMAS` has
best-effort stub field sets for those four. **This needs Munaim to confirm
against Al Shifa Laboratory's actual paper registers** (pathologist presence
log, stock register, reagent inventory, equipment maintenance log) before
it's relied on for real compliance tracking. Not a blocker for pilot
verification — just flag it, don't silently "resolve" it yourself.

---

## Current live state (as of end of this session)

### Docker Compose — running now

```
docker compose ps
```
should show, under project name **`phc-msds-tracker`** (not the directory's
default `phc` — see why below):

| Service | Container | Port (host, 127.0.0.1 only) |
|---|---|---|
| db (Postgres 16) | phc-msds-tracker-db-1 | 5439 → 5432 |
| redis 7 | phc-msds-tracker-redis-1 | 6389 → 6379 |
| backend (Django) | phc-msds-tracker-backend-1 | 8000 → 8000 |
| frontend (Vite dev server) | phc-msds-tracker-frontend-1 | 5173 → 5173 |

**Why the non-default project name and 127.0.0.1-only, non-standard ports:**
this is a shared host running many unrelated production apps (pgsims, rims,
vexel, fmu, class, playgrowth-copilot, and — critically — an existing
**`phc-accreditation`** container which is the live AccrediOps app at
`phc.alshifalab.pk` mentioned in `README.md`). The repo directory is named
`phc`, so `docker compose`'s default project name would have been `phc` too
— and `docker compose up` initially reported the *existing* `phc-accreditation`
and a `phc-web-1` container as **orphans of this project**, meaning Docker
already associated that name with the other, unrelated live app. Port 5432
was also already taken by another Postgres container on this host. Both
`docker-compose.yml`'s `name:` field and every published port were changed to
avoid any collision. **`phc-accreditation` was never stopped or touched** —
verified explicitly during this session. If you bring the stack down/up
again, keep using this compose file as-is; don't let it default back to
project name `phc`.

### Credentials — how to reach it

- Frontend: http://127.0.0.1:5173/ (only reachable from the host machine
  itself — ports are bound to 127.0.0.1, not exposed externally, since no
  public-exposure decision has been made yet — see below).
- Backend API: http://127.0.0.1:8000/api/
- Django admin: http://127.0.0.1:8000/admin/
- Shared login (decision #4): username `alshifa`, password `AlShifa#2026`
  (from `.env`: `SHARED_LOGIN_USERNAME` / `SHARED_LOGIN_PASSWORD`, seeded on
  every container start by
  `backend/apps/registry/management/commands/seed_admin.py` via
  `backend/entrypoint.sh` — idempotent, safe to restart).
- `.env` at repo root (gitignored, not committed) has the real Postgres
  password (generated), a real Django `SECRET_KEY`, and
  `ANTHROPIC_API_KEY=changeme` — **this last one is the blocker, see next
  section.**

### What's already been live smoke-tested successfully

Run from the host, against the running containers:

- **Registry**: `GET /api/registry/indicators/` returns all 118 records live.
- **Evidence — all three `evidence_format` types**, submitted for real via
  `POST /api/evidence/submit/` with Basic auth (`alshifa:AlShifa#2026`):
  - Indicator #1 (photo) — `sign.jpg` uploaded, `is_current=true`.
  - Indicator #4 (document) — `policy.pdf` uploaded, `is_current=true`.
  - Indicator #53 (structured_form) — equipment inventory fields submitted
    (`equipment_name`, `date_of_purchase`, `source`, `date_of_commissioning`).
- **Print pack**: `GET /api/exports/print-pack/` returned a 12-page, 118-entry
  PDF; verified via `pypdf` text extraction that it contained exactly 118
  unique indicator headers in the correct order, and the live overall
  compliance line read `Overall compliance: 2.46% (280.0 / 11380.0 weightage)`
  — matching the three `fully_met` submissions above (100+100+80 = 280 /
  11380 total weightage).

### What's NOT done yet — the actual remaining work

#### Finish the Section B smoke test

`POST /api/drafting/drafts/generate/` was attempted for real against the
Anthropic API and failed cleanly with a `502` and
`"Anthropic API error: ... invalid x-api-key"` — because `.env` still has
`ANTHROPIC_API_KEY=changeme`. This is the **one thing in the entire build
that has not been verified against the real API** (the automated Section B
test suite mocks the Anthropic client, which proves the surrounding business
logic — eligibility, approval, the no-leak rule — is correct, but doesn't
prove a real API call round-trips correctly end to end).

**To finish:**

1. Get a real Anthropic API key from Munaim.
2. Edit `/home/munaim/srv/apps/phc/.env`, replace
   `ANTHROPIC_API_KEY=changeme` with the real key.
3. `docker compose restart backend` (picks up the new env var; the dev
   server's `StatReloader` doesn't reload env vars, only code changes).
4. Run the real end-to-end flow (adjust indicator ID — anything from the
   48-indicator eligible list is fine, e.g. #8, #10, #12 are one-time and
   currently have no evidence):

   ```bash
   AUTH="alshifa:AlShifa#2026"
   BASE="http://127.0.0.1:8000/api"

   # 1. generate for real
   curl -s -u "$AUTH" -X POST $BASE/drafting/drafts/generate/ \
     -H "Content-Type: application/json" -d '{"indicator": 8}'
   # note the returned draft "id"

   # 2. confirm it's NOT in the print pack yet
   curl -s -u "$AUTH" $BASE/exports/print-pack/ -o /tmp/pp_before.pdf
   # extract text with pypdf and grep for a snippet of the draft's content — should be absent

   # 3. approve it
   curl -s -u "$AUTH" -X POST $BASE/drafting/drafts/<id>/approve/ \
     -H "Content-Type: application/json" -d '{"reviewed_by": "Dr. Mubashr Ahmed"}'

   # 4. confirm it's now current evidence AND in the print pack
   curl -s -u "$AUTH" $BASE/evidence/history/8/
   curl -s -u "$AUTH" $BASE/exports/print-pack/ -o /tmp/pp_after.pdf
   # extract text again — the draft's content should now appear under indicator #8
   ```

5. Also worth doing once a key exists: `POST /api/drafting/drafts/bulk_generate/`
   and confirm it only creates drafts for eligible indicators still missing
   current evidence (the automated test already proves this in principle;
   this just confirms the real API round-trip doesn't break it).

#### Cleanup before final verification

During this session, with no API key available, a **placeholder Draft** was
created directly via `docker compose exec backend python manage.py shell` to
demonstrate the approve/print-pack-exclusion mechanism live (not through the
real generate endpoint):

- `Draft.objects.get(id=1)` — indicator #9, kind=`document`, content starts
  with `"[SMOKE TEST — manually seeded, no ANTHROPIC_API_KEY configured] ..."`,
  status is still `draft` (never approved — confirmed absent from a print
  pack pulled while it existed).

**Delete this before treating the pilot as verified** — it's not real AI
output and shouldn't linger:

```bash
docker compose exec -T backend python manage.py shell <<'EOF'
from apps.drafting.models import Draft
Draft.objects.filter(id=1, content__startswith="[SMOKE TEST").delete()
EOF
```

Separately, decide with Munaim whether to **keep or clear** the three real
evidence submissions made during smoke testing (indicators #1, #4, #53 —
listed above). They're real, valid submissions through the real API, just
not actual lab evidence. Options: leave them as a demo/proof-of-life state,
or reset via `docker compose down -v && docker compose up -d --build` (drops
the Postgres volume, re-migrates, re-seeds indicators + LabProfile + shared
login from scratch — but also wipes any other evidence entered in the
meantime, so check with Munaim first if this is genuinely a shared pilot by
then).

#### Public exposure via Caddy — needs explicit go-ahead

Right now everything is bound to `127.0.0.1` only — not reachable outside
this machine. This host runs a **shared, live production Caddy instance**
(`systemctl status caddy` — active, serving other real apps: AccrediOps,
FMU platform, RadReport, etc., per `/etc/caddy/Caddyfile` and
`/home/munaim/srv/proxy/caddy/Caddyfile`). If/when Munaim wants this
reachable at a real subdomain, that means editing shared infrastructure that
other live sites depend on — **do not do this without explicit confirmation
and a specific subdomain from Munaim**, and when you do, treat the Caddyfile
edit with the same care as a production deploy (back it up, validate config
before reload, `systemctl reload caddy` not `restart`). This was
intentionally left undone this session — it's a shared-infra change, not a
pilot-readiness item, and wasn't asked for explicitly.

---

## Reference — commands you'll want

```bash
# from /home/munaim/srv/apps/phc

# full backend test suite (34 tests, should all pass)
cd backend && export USE_SQLITE=True && ./venv/bin/python manage.py test

# check container status / logs
docker compose ps
docker compose logs backend --tail 50
docker compose logs frontend --tail 50

# restart backend after an .env change
docker compose restart backend

# django shell inside the running container
docker compose exec backend python manage.py shell

# local venv (host-side, sqlite) — separate from the docker postgres DB,
# useful for quick checks without touching the live pilot data
cd backend && export USE_SQLITE=True && ./venv/bin/python manage.py shell
```

Key files if you need to change anything:
- `docker-compose.yml` — project name `phc-msds-tracker`, all ports pinned to
  127.0.0.1.
- `.env` (repo root, gitignored) — real secrets for the running pilot.
- `backend/entrypoint.sh` — migrate → load_indicators → seed_admin → runserver,
  runs on every container start, all idempotent.
- `docs/status/PARKED_DECISIONS.md` — one open entry (#1, structured_form
  fields).
- `docs/status/DEVELOPMENT_STATUS.md` — points back here.

## Suggested prompt for the next agent (verification session)

> Read `HANDOFF.md` at the repo root in full before doing anything else — it
> has complete context on the PHC MSDS Compliance Tracker build that just
> finished. Munaim is asking you to verify the build and application
> readiness. Don't rebuild anything that's already done and quality-gated —
> confirm it's still true (re-run the test suite, check the containers are
> still healthy) rather than re-deriving it from scratch. The concrete
> remaining work is in `HANDOFF.md` under "What's NOT done yet": finish the
> Section B live smoke test once Munaim provides a real
> `ANTHROPIC_API_KEY`, clean up the placeholder smoke-test Draft, and confirm
> with Munaim whether to keep or clear the demo evidence entries before
> calling the pilot done. Do not touch `/etc/caddy/Caddyfile` or expose
> anything publicly without Munaim's explicit go-ahead. Report back with a
> clear pass/fail against every Quality Gate in `BUILD_PROMPT.md` and the
> smoke-test checklist in the original build prompt — verified, not
> "should work."
