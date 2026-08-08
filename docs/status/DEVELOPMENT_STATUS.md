# Development Status

Update this file as each stage completes — don't let it go stale.

## Current stage: Feature-complete against Master Build Prompt (2026-08-07)

Stage 0, Stage 1, Stage 2, and Section B are implemented. The automated quality-gate suite is in `backend/apps/registry/tests.py`.

## Stage checklist

- [x] Stage 0 — Indicator Registry + Lab Profile
- [x] Stage 1 — Recurring Entry + Daily Due-List + Compliance Scoring
- [x] Stage 2 — Print/Export Engine
- [x] Section B — AI Drafting Assistant

## Notes

(Add dated entries here as work progresses — what changed, what's blocked, what
needs a decision from Munaim.)

### 2026-08-07 — Master build run

Implemented the registry, recurring evidence and presence-only due list, live
weightage scoring, full 118-indicator PDF print pack, and human-reviewed draft
workflow. Backend tests: 4 passed; frontend `npm run build`: passed.

Quality-gate note: structured-form field schemas for five indicators remain
deferred under parked decision #1. The app uses a generic JSON payload editor
until those exact fields and validation rules are decided; no field names were
invented.

### 2026-08-07 — Phase 1 compliance run: one-time indicator SOPs drafted

All 32 one-time indicators mapped to 17 documents and drafted (grouped
logically, e.g. specimen collection→disposal as one SOP rather than six).
Staged at `docs/evidence/one_time/` (not yet wired to an Evidence app — Stage
0 hasn't started, see stage checklist above). See `docs/evidence/README.md`
for the staging convention and `docs/evidence/one_time/manifest.json` for the
doc→indicator mapping.

**Outstanding before these can be reviewed/signed and moved to
`approved_filed`:**
- ASL-POL-11 (QA Program) — EQA scheme name left open by Munaim's choice, to be filled in later
- ASL-SOP-14 (Waste Management) — signed contract copy + Safe Waste
  Disposal's license/registration number not yet attached
- ASL-SOP-15 (First Aid) — nearest hospital name/contact not yet entered

**Not blocked, just not started:** Phase 2 (57 recurring indicator
templates) and Phase 3 (29 physical indicator gap checklist).

### 2026-08-07 — Phase 2 compliance run: recurring indicator templates drafted

All 57 recurring indicators mapped to 29 register/log templates and drafted
(grouped logically, e.g. equipment log book + maintenance record + inventory
as one document rather than four). Staged at `docs/evidence/recurring/`,
same convention as Phase 1 — see `docs/evidence/README.md` and
`docs/evidence/recurring/manifest.json`.

Each template includes the register/log format plus one filled example
entry. The template document itself needs review/approval like Phase 1; the
**ongoing dated entries within each register are the actual recurring
evidence**, generated as the lab operates — not something this drafting run
can produce, by definition.

**Outstanding before these can be reviewed/signed:**
- ASL-REC-06 — no satellite collection centres currently (register ready, unused)
- ASL-REC-10 — current fire/non-fire detection provisions not yet confirmed (physical item, Phase 3)
- ASL-REC-20 — actual current price list not yet entered
- ASL-REC-22 — EQA scheme provider name not yet entered (open by Munaim's choice — same item as ASL-POL-11)
- ~~ASL-REC-27 — specific LIS product/vendor name not yet entered~~ **Resolved 2026-08-07: Xmed EMR/LIMS** — also updated in ASL-REC-28 and ASL-REC-29's references.
- ASL-REC-28 — notifiable disease list not yet confirmed against current Punjab/national requirements
- ASL-REC-29 — whether Xmed EMR/LIMS supports a patient-facing report access code not yet confirmed

**Not blocked, just not started:** Phase 3 (29 physical indicator gap checklist).
