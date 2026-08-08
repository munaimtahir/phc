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

(none yet)

### #1 — Structured evidence field schemas

- Stage/component: Stage 1, structured-form entry fields for five indicators
- Hit during: building the evidence entry form
- Why it's ambiguous: the locked pack specifies `structured_form` and says to use the exact field set implied by each indicator's requirements, but it does not define a canonical field schema for these five records.
- Stub implemented: a structured JSON payload editor in `frontend/src/components/EvidenceEntryForm.tsx`; backend stores the submitted JSON without inventing field names.
- What needs deciding: the field names, types, and validation rules for each structured-form indicator.
- Status: OPEN
