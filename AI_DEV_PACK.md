# AI Dev Pack — PHC MSDS Compliance Tracker
Private Laboratory · PHC Licensing · Clinical/Pathology MSDS Reference Manual

Status: **All decisions locked. Build-ready for Stage 0.**

---

## 1. What was extracted from the manual

Source: `biik.docx` — PHC MSDS Reference Manual, Clinical/Pathology Laboratories.

Parsed and verified against the manual's own summary numbers:

| Item | Count | Verified against manual text |
|---|---|---|
| Domains | 10 | ROM, FMS, HRM, MER, RRS, QA, BSBS, AAC, COP, PRE |
| Standards | 37 | "comprising of 37 basic standards" ✓ |
| Indicators | 118 | "118 associated indicators" ✓ |
| Full-compliance indicators (100% weightage) | 97 | "97 requiring full compliance...100% weightage" ✓ |
| Partial-compliance indicators (80% weightage) | 21 | "21 acceptable...80% weightage" ✓ |

Every indicator was captured with: domain, standard code, standard title, indicator text, survey process (what the assessor checks), compliance requirements (what must exist), scoring criteria (fully met / partially met / not met), and weightage.

**This confirms the AccrediOps 118-indicator model already deployed at `phc.alshifalab.pk` is built on the correct, complete source data** — this pack extends it with per-indicator recurring-evidence tracking and the print pack, rather than replacing the model.

## 2. A scoring detail this surfaced that we hadn't discussed yet

The manual scores each indicator on a 3-tier scale, not a simple done/not-done:

- **Fully met** → full weightage (100% or 80%, per indicator)
- **Partially met** → only for the 21 flagged indicators, scored at 80%
- **Not met** → 0

This matters for the app: "100% compliance" isn't just "every indicator has evidence uploaded" — it's the earned-weightage sum across all 118 divided by the possible weightage sum.

**Locked:** every recurring evidence entry captures fully_met / partially_met / not_met, matching PHC's own self-assessment process. Overall compliance % is computed as earned weightage ÷ possible weightage across all 118, live at any time.

## 3. Decisions locked so far (from our discussion)

- Indicator taxonomy: **physical** (static evidence, photo/attachment) · **one-time** (SOPs/policies, revised every 2–3 yrs, latest version only retained) · **recurring** (daily/weekly/monthly/biannual/annual, evidence retained ~1 year, configurable)
- Auth: single shared login, MVP scope (2–3 staff)
- Print pack: single action compiling the full current indicator set with latest evidence, **ordered to mirror PHC's own domain → standard → indicator numbering** (so it reads as the assessor's own checklist)
- Recurring evidence status: **fully_met / partially_met / not_met captured per entry** (see §2)
- Daily indicators: **lab operates 7 days/week** — due-list generates every day, no weekend skip
- **No on-time/late tracking on entries.** The due-list is a simple presence check — "has this period's evidence been entered yet, yes/no" — not a deadline calculation. An entry made the next morning, or mid-period, counts the same as one made right on the day; there's no separate "late" state or penalty. The due-list exists to remind staff what still needs doing, not to police exactly when they did it.

## 4. Classification — finalized

You accepted the rule-based draft as-is for 102 indicators. The 16 flagged `needs_review` (no confident keyword match) needed an actual judgment call rather than defaulting to something arbitrary, so I classified those manually and logged the reasoning against each one — e.g. Ind. 100 ("facilitated toilets for disabled patients") → `physical`; Ind. 66 (external quality assessment) → `recurring`, `quarterly`.

Three of those needed frequency values outside the original enum — added `quarterly` (external QA participation, QA gap reviews) and `as_needed` (new-hire orientation acknowledgment, which is event-triggered rather than calendar-based) to the frequency set.

**`indicators_master.json` is now the canonical, locked indicator registry** — every one of the 118 indicators has a final `category`, `frequency`, and `evidence_format`, plus a `classification_source` (`rule_based_accepted` or `manual_override`) and `classification_note` where a manual call was made, so the reasoning stays visible rather than disappearing into the data.

## 5. Data model (draft — reflects the manual's actual structure)

```
Domain            id, code (e.g. "ROM"), name
Standard          id, domain_id, standard_no, code (e.g. "ROM-1"), title
Indicator         id, standard_id, text, weightage (100|80), allows_partial (bool),
                  category (physical|one_time|recurring),
                  frequency (nullable; daily|weekly|monthly|quarterly|biannual|annual|as_needed),
                  evidence_format (photo|document|structured_form),
                  compliance_requirements (text), survey_process (text) — reference only,
                  retention_months (nullable, default from category)

EvidenceRecord    id, indicator_id, period_label (nullable — only for recurring),
                  submitted_at, submitted_by,
                  status (fully_met|partially_met|not_met),
                  payload (file and/or structured form fields),
                  is_current (bool — true for the one live record on physical/one-time indicators)

ComplianceSnapshot (computed, not stored)
  per indicator: current status + evidence age
  overall: earned weightage / possible weightage across all 118
```

Physical and one-time indicators keep exactly one `is_current=true` EvidenceRecord, replaced on re-upload. Recurring indicators accumulate one EvidenceRecord per period, pruned past the retention window.

## 6. Open decisions

None remaining. Everything needed for Stage 0 is locked (§3, §4, §5, §8).

**Locked:** evidence format is a mix, per indicator — some recurring indicators are structured digital fields (e.g. fridge temperature: date/time/value/initials, enabling automatic out-of-range flags), others stay as a photo of the existing paper log or a document upload. This is now a third editable column in the same xlsx review sheet (§4) rather than a separate pass — no need to touch it twice.

## 7. Proposed stage-gated build order

Matches your usual pattern — mock/no-write first, lock each stage before the next.

**Stage 0 — Indicator Registry**
Load all 118 indicators (once §4 is confirmed) into the data model above. No entry, no scheduling, no print. Just prove the registry renders correctly, filterable by domain/standard/category.

**Stage 1 — Recurring Entry + Daily Due-List**
The daily habit loop: for each recurring indicator, the due-list shows whether current-period evidence exists yet — a simple presence check per period_label, no deadline/lateness logic. Staff submit evidence (fully/partially/not_met + payload), auto-filed under the right indicator. Depends on §1, §3 decisions being locked.

**Stage 2 — Print/Export Engine**
Compile-to-paper for the PHC visit. Depends on §4 decision.

Each stage gets its own scoped prompt for the AI coding agent once locked — I haven't written those yet since two of the three stages still depend on open decisions above.

## 8. Section B — AI Drafting Assistant (new module, parallel to the tracker)

Distinct from the tracker (§1-8) but consumes the same indicator data — specifically each indicator's `compliance_requirements` and `survey_process` text, which is exactly what PHC's assessor checks against. This grounds drafts in the actual requirement rather than a generic template.

**Locked scope:**
- Drafts for **one-time/policy indicators** (SOPs, policies, plans — ~30 indicators) **and templates for recurring documentary indicators** (meeting minutes format, training record format, etc.) — not physical indicators.
- Generation triggerable **both on-demand** (single indicator) **and in bulk** (all missing/eligible indicators at once).

**Design implication worth flagging — two different draft objects, not one:**

- **One-time indicators** → AI drafts the actual full document (e.g. the Emergency Policy itself). On approval, it *becomes* that indicator's current evidence.
- **Recurring documentary indicators** → AI drafts a reusable *template/format* (e.g. "Monthly QC Meeting Minutes" with the fields PHC's indicator requires — date, attendees, agenda items covered). Staff then fill that template in each period; the filled instance is the recurring EvidenceRecord, not the template itself.

**Human-in-the-loop, non-negotiable:** every generation lands as `status=draft`. Nothing becomes `is_current` evidence without an explicit human approval action — no auto-publish, no auto-file. This matters practically, not just as a safety habit: PHC is assessing *your* institutional documents, and an unreviewed AI draft filed as evidence is a liability, not a compliance win.

```
Draft             id, indicator_id, kind (document|template), content, generated_at,
                  status (draft|approved|rejected), reviewed_by, reviewed_at, version_no
```
On approval: `document` drafts replace the indicator's current EvidenceRecord; `template` drafts become the structure recurring EvidenceRecords are filled against.

**Locked:** Lab Profile confirmed as a foundational data object — one-time setup, referenced by every AI generation prompt so drafts name the actual institution instead of placeholders.

```
LabProfile        lab_name, address, phc_registration_no, supervising_pathologist,
                  (extendable later: section heads, equipment list, staff roster —
                  not needed to start, add as specific drafts require them)
```

Seed values on file:
- Lab name: Al Shifa Laboratory
- Address: Circular Road, Jaranwala
- PHC Registration No.: P-20787
- Supervising Pathologist: Dr. Mubashr Ahmed

This is a small, fixed set of fields for now — enough for most one-time SOPs/policies to reference correctly. Anything a specific draft needs beyond this (e.g. an equipment list for a maintenance SOP) gets added to the profile incrementally rather than front-loading a large form nobody's asked for yet.

## 9. Stage 0 — Build Prompt

Ready to hand to Claude Code (or similar) as-is. Scoped tight per your usual pattern: registry only, no entry/scheduling/print logic yet.

```
Build Stage 0 of the PHC MSDS Compliance Tracker: the indicator registry, nothing more.

Scope — build exactly this, no more:
1. Load /indicators_master.json (118 records) into the data model below.
2. A LabProfile record, seeded with:
   - lab_name: Al Shifa Laboratory
   - address: Circular Road, Jaranwala
   - phc_registration_no: P-20787
   - supervising_pathologist: Dr. Mubashr Ahmed
3. A read-only registry view: list all 118 indicators, filterable by domain,
   standard, category (physical/one_time/recurring), and frequency.
   Show weightage and allows_partial per indicator.
4. Nothing else. No evidence entry, no due-lists, no scoring computation,
   no print/export, no auth beyond a single shared login stub.

Data model — Domain, Standard, Indicator (id, standard_id, text, weightage,
allows_partial, category, frequency, evidence_format, compliance_requirements,
survey_process, retention_months), LabProfile — per the AI Dev Pack §5, §9.

Do not invent business rules beyond what's specified above or in the source
JSON. If something is ambiguous, stop and ask rather than assuming.

Definition of done: registry renders all 118 indicators correctly, filters work,
LabProfile is stored and editable, and a spot-check against indicators_master.json
confirms no data was dropped or altered in transit.
```

## 10. Files in this pack

- `indicators_master.json` — canonical, locked indicator registry (118 indicators, all manual fields + final category/frequency/evidence_format + classification source/notes for the 16 manually-resolved ones)
- `MSDS_Indicator_Classification_Review.xlsx` — working review sheet (superseded by indicators_master.json, kept for reference)
- This document
