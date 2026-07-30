# 0003 — Decision Points: Park, Don't Stop

Status: Locked. Supersedes the "stop the run and ask" fallback in
`BUILD_PROMPT.md` v2 for genuine decision points (not for the two
non-negotiable rules, which are unaffected — see below).

## What changed

Previously: hitting a business-rule gap not covered by the pack meant
stopping the entire build run for a human decision. For a single unattended
run, one ambiguous field could otherwise block everything built after it.

Now: the agent implements the smallest safe stub for that one piece, logs it
in `docs/status/PARKED_DECISIONS.md` with enough context to resolve later,
and continues building everything else that doesn't depend on it. Affected
Quality Gate checks are marked "Deferred (parked #n)," not Pass or Fail.

## What did NOT change

The two non-negotiable rules are not decision points and are never parked:
1. No silent invention of a rule *already decided* in `AI_DEV_PACK.md` or
   `docs/decisions/` — parking is for genuine gaps, not a way to defer
   something already answered.
2. No automatic publishing in Section B — a permanent runtime rule, not a
   build-time checkpoint, and not stub-able.

## Reviewing parked items

`docs/status/PARKED_DECISIONS.md` is the single place to check after a build
run — resolve everything there in one pass rather than one at a time.
