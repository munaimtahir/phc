# Master Build Prompt — PHC MSDS Compliance Tracker
(v2 — quality-gated, single run. Supersedes the per-stage check-in version;
see `docs/decisions/0002-frequency-resolution-and-quality-gates.md`.)

Hand this whole document to the coding agent working in the `phc` repository.
Build Stage 0 → Stage 1 → Stage 2 → Section B in one run. **Do not stop for
human confirmation between stages** — instead, verify each stage against its
Quality Gate below, and only proceed once every check in that gate passes.
If you hit a genuine decision point along the way, **park it and keep going**
— see "Decision Points: Park, Don't Stop" below — rather than halting the
whole run over one ambiguous item.

Read `README.md`, `AGENTS.md`, `AI_DEV_PACK.md`, and everything in
`docs/decisions/` before starting. `docs/data/indicators_master.json` is the
canonical 118-indicator registry — never hand-edit or regenerate it.

---

## Decision Points: Park, Don't Stop

If you hit a genuine decision point — a case not covered by `AI_DEV_PACK.md`
or `docs/decisions/`, where proceeding would mean inventing a business rule —
do **not** stop the whole build run. Instead:

1. Implement the smallest safe placeholder/stub for that specific piece only
   — something that lets the rest of the system keep working without
   asserting the undecided rule as final. Mark it clearly in code, e.g.
   `# PARKED: see docs/status/PARKED_DECISIONS.md #<n>`.
2. Log it in `docs/status/PARKED_DECISIONS.md`: what was hit, which
   stage/component, why it's ambiguous, what stub you implemented instead,
   and what actually needs a human decision.
3. Continue building everything else in that stage and subsequent stages
   that doesn't depend on the parked item.
4. In that stage's Quality Gate report, mark any check blocked by the parked
   item as "Deferred (parked #n)" — not Pass, not Fail. Don't count it as a
   failure that stops the run, and don't fake a pass either.

At the end of the full run, report every parked item in one place, so they
can all be resolved together rather than trickling back one at a time.

## Two rules that are NOT quality-gated, and NOT park-able

These are not decision points and never go in the parking log. A passing
quality gate never overrides them, and neither does parking.

1. **No silent business-rule invention of anything already decided.** The
   parking mechanism above exists for genuinely *undecided* specifics — it is
   not a way to defer something this pack already answers. If it's in
   `AI_DEV_PACK.md` or `docs/decisions/`, use it; don't park it.
2. **No automatic publishing in Section B.** An AI-generated draft becomes
   filed evidence only via an explicit human approval action. This is a
   permanent runtime behavior of the app, not something that gets relaxed
   once tests are green, and not something to stub around "for now."

If either of these would be violated to make a gate pass or to unblock a
parked item, the implementation has been built wrong — fix it, don't loosen
the rule.

---

## Stage 0 — Indicator Registry + Lab Profile

**Scope:**
1. Load `docs/data/indicators_master.json` (118 records) into the data model.
2. `LabProfile`, seeded with: lab_name "Al Shifa Laboratory", address
   "Circular Road, Jaranwala", phc_registration_no "P-20787",
   supervising_pathologist "Dr. Mubashr Ahmed".
3. Read-only registry view, filterable by domain, standard, category,
   frequency. Show weightage and allows_partial.
4. Nothing else yet — no entry, no due-lists, no scoring, no export.

**Data model:**
```
Domain            id, code, name
Standard          id, domain_id, standard_no, code, title
Indicator         id, standard_id, text, weightage (100|80), allows_partial,
                  category (physical|one_time|recurring),
                  frequency (null|daily|weekly|monthly|quarterly|biannual|annual|as_needed),
                  evidence_format (photo|document|structured_form),
                  compliance_requirements, survey_process, retention_months
LabProfile        lab_name, address, phc_registration_no, supervising_pathologist
```

**Quality Gate — all must pass before starting Stage 1:**
- [ ] Exactly 118 Indicator records exist; IDs are exactly `{1..118}`, no gaps, no duplicates.
- [ ] Per-domain counts match exactly: AAC 9, BSBS 18, COP 6, FMS 11, HRM 16, MER 13, PRE 7, QA 16, ROM 13, RRS 9.
- [ ] Exactly 37 distinct Standard records.
- [ ] Weightage split is exactly 97 indicators @ 100, 21 @ 80 (`allows_partial=true` count == 21).
- [ ] Category split is exactly physical 29, one_time 32, recurring 57.
- [ ] Every `category=recurring` indicator has a non-null `frequency`; every `category` in {physical, one_time} has `frequency=null`.
- [ ] `evidence_format` split is exactly photo 69, document 44, structured_form 5.
- [ ] For 10 spot-check indicator IDs chosen at random, `indicator_text`, `compliance_requirements`, and `weightage` in the database match the source JSON byte-for-byte.
- [ ] LabProfile record exists with all four seed fields populated exactly as given above (no placeholder text).
- [ ] Registry view filter by `domain=ROM` returns exactly 13 records; filter by `category=recurring` returns exactly 57.

If any check fails: fix and re-run the full gate — do not proceed on a partial pass.

---

## Stage 1 — Recurring Entry + Daily Due-List + Compliance Scoring

**Scope:**
1. `EvidenceRecord` (below). Physical/one-time indicators keep exactly one
   `is_current=true` record, replaced on re-upload. Recurring indicators
   accumulate one record per `period_label`:
   - daily → `YYYY-MM-DD`, weekly → `YYYY-Www`, monthly → `YYYY-MM`,
     quarterly → `YYYY-Qn`, biannual → `YYYY-H1`/`YYYY-H2`, annual → `YYYY`.
   - `as_needed` indicators are event-triggered, not period-keyed — log each
     occurrence with its timestamp, no due-list entry generated for these.
2. **Due-list:** for every recurring indicator except `as_needed`, show
   whether the current period already has a record — presence check only,
   no deadline/lateness logic (decision #7). Daily indicators regenerate
   every day, 7 days/week (decision #6).
3. **Entry form** per `evidence_format`: `structured_form` → digital fields
   (if an indicator's exact field set isn't obvious from its
   `compliance_requirements` text, that's a genuine gap — stop and ask,
   don't invent fields); `photo`/`document` → file upload. Every entry
   captures `status`: fully_met / partially_met (only if `allows_partial`) /
   not_met.
4. **Retention:** recurring records older than `retention_months` (default
   12) are pruned. Physical/one-time indicators keep only the current record.
5. **Compliance scoring:** overall % = (Σ earned weightage) ÷ (Σ possible
   weightage) across all 118. Earned weightage per indicator = weightage if
   latest record's status is fully_met; weightage × 0.8 if partially_met
   (only where `allows_partial`); 0 if not_met or no record exists. Uses each
   indicator's **most recent** record, not specifically the current period's.

**Data model addition:**
```
EvidenceRecord    id, indicator_id, period_label (nullable for as_needed),
                  submitted_at, submitted_by, status (fully_met|partially_met|not_met),
                  payload (file ref and/or structured field values), is_current
```

**Quality Gate — all must pass before starting Stage 2:**
- [ ] Fixture test: insert a known set of EvidenceRecords across ≥10 indicators covering all three statuses; computed compliance % matches a hand-calculated expected value to within rounding.
- [ ] Due-list for a fixed test date returns exactly the recurring (non-`as_needed`) indicators with no record for that date's period — verified against a hand-built fixture, not just "runs without error."
- [ ] An indicator with `category` in {physical, one_time} never appears on the due-list.
- [ ] An `as_needed` indicator never appears on the due-list regardless of record history.
- [ ] Retention test: a recurring record older than its indicator's `retention_months` is pruned by the retention job; a physical/one-time indicator's sole current record is never pruned regardless of age.
- [ ] Entry form renders the correct input type for each of the three `evidence_format` values — verified for at least one indicator of each type.
- [ ] `partially_met` is not selectable/acceptable on an indicator where `allows_partial=false` — attempt it in a test and confirm it's rejected.
- [ ] No `EvidenceRecord` exists for a recurring (non-`as_needed`) indicator with a null `period_label`.

---

## Stage 2 — Print/Export Engine

**Scope:**
1. Single action compiling all 118 indicators with current evidence into a
   print-ready PDF.
2. Ordering mirrors PHC's own domain → standard → indicator numbering
   (decision #8) — same order as `indicators_master.json`.
3. Per indicator: text, weightage, current status, and the evidence itself
   (embedded image / rendered content / attached file per its
   `evidence_format`).
4. Overall compliance % (from Stage 1) as a summary at the top, computed
   live at export time — not cached/hardcoded.

**Quality Gate — all must pass before starting Section B:**
- [ ] Exported document contains exactly 118 indicator entries — no omissions, no duplicates.
- [ ] Entry order exactly matches `indicators_master.json`'s domain → standard → indicator sequence (assert against the precomputed expected ID sequence, not eyeballed).
- [ ] An indicator with no current evidence still appears in the export, explicitly marked as such — never silently dropped.
- [ ] The compliance % shown in the export matches Stage 1's live-computed value at generation time (regenerate evidence, re-export, confirm the number changes accordingly — it must not be a stale/cached figure).
- [ ] Export succeeds end-to-end for the full 118-indicator set in one action, no manual per-indicator compilation step.

---

## Section B — AI Drafting Assistant

**Scope (decisions #11, #12, #13):**
- Drafts for one-time/policy indicators (32) and templates for recurring
  documentary indicators — never for physical indicators.
- Generation triggerable both on-demand and in bulk (all indicators
  currently missing current evidence, within the eligible scope above).
- Every generation lands as `status=draft`. Human approval required before
  anything becomes filed evidence — see the non-negotiable rule at the top
  of this document.

**Data model addition:**
```
Draft             id, indicator_id, kind (document|template), content,
                  generated_at, status (draft|approved|rejected),
                  reviewed_by, reviewed_at, version_no
```

**Generation:** Anthropic API (`ANTHROPIC_API_KEY` from `.env`), grounded in
the target indicator's `compliance_requirements` + `survey_process` plus
`LabProfile` fields, so drafts name Al Shifa Laboratory / Circular Road,
Jaranwala / P-20787 / Dr. Mubashr Ahmed directly.

**Two draft kinds:** `document` (one-time indicators) → on approval, replaces
that indicator's current `EvidenceRecord`. `template` (recurring documentary
indicators) → on approval, becomes the structure future `EvidenceRecord`
entries for that indicator are filled against — never itself evidence.

**Quality Gate — all must pass before calling the build complete:**
- [ ] **Critical:** no `Draft` with `status=draft` or `status=rejected` is ever readable from any evidence/print-pack query path. Write this as an explicit automated test, not a manual check — this is the single most important gate in the whole build.
- [ ] Approving a `document` draft correctly sets it as the target indicator's `is_current` evidence, and the previous current record is superseded (not deleted, unless that matches Stage 1's retention behavior for one-time indicators).
- [ ] Approving a `template` draft makes it retrievable as that indicator's entry structure, and does **not** create or modify any `EvidenceRecord`.
- [ ] `Draft.status=approved` records always have non-null `reviewed_by` and `reviewed_at` — attempt to approve without them and confirm it's rejected.
- [ ] Bulk generation creates drafts only for indicators within scope (one-time + recurring-documentary) that currently lack current evidence — an indicator that already has current evidence is skipped, not overwritten with a fresh draft.
- [ ] A generated draft never appears in a Stage 2 print export unless it has been approved.

---

## After Section B's gate passes

The build is feature-complete against this pack. Report a final summary:
which quality-gate checks were run, confirmation all passed, and anything
that had to stop for a decision along the way (per the non-negotiable rules
above). Anything beyond this scope — multi-user roles, notifications, mobile
app, multi-lab support — is new scope requiring its own discussion.
