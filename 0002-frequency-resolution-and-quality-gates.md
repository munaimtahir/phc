# 0002 — Frequency Resolution + Quality-Gate Build Policy

Status: Locked.

## Frequency resolution

The 42 recurring indicators left as `periodic_unspecified` after the xlsx
review (accepted as-is) had no calendar cadence assigned — the PHC manual
itself doesn't mandate one for these, since it's a survey/accreditation
document, not an operations manual. Each was assigned a specific frequency
by judgment (annual/monthly/quarterly/daily/weekly/as_needed), logged per
indicator in `docs/data/indicators_master.json` as `classification_source:
manual_override` with a `classification_note` explaining the call.

Final recurring frequency distribution: annual 18, monthly 18, quarterly 8,
as_needed 7, daily 4, weekly 1, biannual 1.

These are more debatable than the physical/one-time/recurring category calls
(§4 of `AI_DEV_PACK.md`) — flag any that don't match how you actually want to
run the lab, and they can be corrected same as the category overrides were.

## Build policy change — quality gates replace per-stage check-ins

Superseding the "stop after every stage for human confirmation" rule in the
original `BUILD_PROMPT.md`/`AGENTS.md`: the agent now verifies each stage
against an explicit, automated **quality gate** (see `BUILD_PROMPT.md`) and
proceeds to the next stage on its own once the gate passes — no human
check-in required between stages.

**What did NOT change:**
- No silent business-rule invention. Quality gates verify *already-decided*
  rules are correctly implemented — they are not a substitute for deciding
  something that was never decided. If the agent hits a genuine gap (a rule
  not covered by `AI_DEV_PACK.md` or the decisions log), it still stops and
  asks. This is a different thing from a stage checkpoint and is not being
  relaxed.
- No automatic publishing in Section B. The human-approval-before-evidence
  rule is a runtime product behavior, not a development-time checkpoint —
  it doesn't get built once and then relaxed for convenience. It gets its
  own quality gate instead (see `BUILD_PROMPT.md` § Section B).
