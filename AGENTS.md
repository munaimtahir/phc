# Agent Operating Rules

Read this before writing any code in this repository.

## Stage-gated, but self-verifying (v2)

Work is organized into explicit stages (see `BUILD_PROMPT.md`), each with its
own **Quality Gate** — a concrete, automated checklist. Verify a stage against
its gate and, if every check passes, proceed to the next stage on your own.
Human check-in between stages is no longer required — see
`docs/decisions/0002-frequency-resolution-and-quality-gates.md` for why this
changed from the original per-stage confirmation model.

If a gate check fails, fix it and re-run the full gate. Do not proceed on a
partial pass, and do not narrow a gate's criteria to make it pass.

If instead you hit a genuine decision point (not a failing gate — an actual
gap the pack doesn't answer), don't stop the run either: park it with a safe
stub and keep going. Full mechanism in `BUILD_PROMPT.md` § Decision Points:
Park, Don't Stop.

## Two things quality gates do NOT cover

These are not decision points to park, and gates never override them:

1. **No silent business-rule invention of anything already decided.** A
   quality gate verifies an *already-decided* rule was built correctly — it
   is not a substitute for a decision that was never made, and parking is
   not a way to defer something this pack already answers. If a case is
   genuinely undecided, park it (see `BUILD_PROMPT.md` § Decision Points:
   Park, Don't Stop) rather than inventing a rule or halting the whole run.
2. **No automatic publishing**, most importantly in Section B. A generated
   document or template is a `Draft` with `status=draft` until a human
   explicitly approves it. This is enforced by its own quality gate, but it
   is also a hard rule independent of that gate — don't build a path that
   skips it, and don't "park" your way around it either.

## Data integrity

`docs/data/indicators_master.json` is the canonical, locked indicator registry
(118 records). Do not hand-edit it. Do not regenerate it from the source MSDS
manual — that extraction and classification work is already done and reviewed.
If the loader needs to transform it, do so in code, leaving the source file
untouched.

## Definition of done, per stage

Each stage prompt in `AI_DEV_PACK.md` §9 includes its own "definition of done."
Don't mark a stage complete until every item in that list is verifiably true —
spot-check against the source data, don't just confirm the code runs.

## When in doubt

Prefer stopping and asking over shipping a guess. A stalled stage costs a
question; a wrong assumption baked into the compliance model costs trust in
the whole system's numbers.
