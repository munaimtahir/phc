# Parked Decisions

Append-only log. One entry per decision point hit during the build that
`AI_DEV_PACK.md` / `docs/decisions/` didn't answer. Do not delete entries once
resolved — mark them resolved and keep the history.

Never park the two non-negotiable rules (silent rule invention of anything
already decided; automatic publishing in Section B) — see `BUILD_PROMPT.md`.
Those aren't decision points, they don't belong in this log, and hitting one
means stop, not park.

## Template — copy per entry

```
### #<n> — <short title>

- Stage/component: <e.g. Stage 1, structured_form field set for Ind. 91>
- Hit during: <what you were building when you hit this>
- Why it's ambiguous: <what AI_DEV_PACK.md / docs/decisions/ don't answer>
- Stub implemented: <the safe placeholder you built instead, and where it
  lives in the codebase>
- What needs deciding: <the actual question for Munaim, phrased so it can be
  answered directly>
- Status: OPEN | RESOLVED (<date>, <what was decided>)
```

## Entries

### #1 — structured_form exact field sets for indicators 6, 44, 46, 50

- Stage/component: Stage 1, `apps/evidence/structured_forms.py` (entry form field
  schemas for `evidence_format=structured_form` indicators).
- Hit during: building the digital entry form for the 5 `structured_form`
  indicators (6, 44, 46, 50, 53).
- Why it's ambiguous: BUILD_PROMPT.md says a structured_form indicator's field
  set should come from its `compliance_requirements` text when obvious.
  Indicator 53 spells its fields out explicitly (date of purchase, source,
  date of commissioning, calibration dates) and was implemented directly from
  that text — not parked. Indicators 6, 44, 46 and 50 only describe the
  *existence* of a register/log ("up-to-date stock registers", "up-dated
  inventory of stored reagents", "log books contain record of...
  maintenance") without listing the actual columns the lab's real paper
  registers use.
- Stub implemented: best-effort field sets in
  `apps/evidence/structured_forms.py::STRUCTURED_FORM_SCHEMAS` for indicators
  6, 44, 46, 50 (e.g. #44 stock register: date/item/qty received/qty
  issued/remarks), inferred from the requirement wording, not from the lab's
  actual register format.
- What needs deciding: Munaim should confirm these field sets against the
  actual paper registers currently used at Al Shifa Laboratory for: pathologist
  presence log (#6), stock register (#44), reagent inventory (#46), and
  equipment maintenance log (#50) — and we adjust the schema to match exactly.
- Status: OPEN
