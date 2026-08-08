# Evidence Staging Area

This folder holds documents produced by the Phase 1/2/3 AI-assisted compliance
runs, staged here **ahead of** the Evidence app (`backend/apps/evidence`)
being built. Nothing in here is filed compliance evidence yet — see
`AGENTS.md`'s "No automatic publishing" rule.

## Layout

```
docs/evidence/
  one_time/          Phase 1 — one-time indicator SOPs/policies (32 indicators, 17 docs)
    manifest.json    Doc → indicator_id mapping, version, status, outstanding placeholders
    *.docx           The drafted documents themselves
  recurring/         Phase 2 — recurring indicator templates (not yet generated)
  physical/          Phase 3 — physical/infrastructure gap checklist (not yet generated)
```

## Status convention

Every entry in a `manifest.json` carries a `status`:

- `draft_pending_approval` — AI-drafted, not yet reviewed or signed. **Not valid evidence.**
- `approved_filed` — Signed by both Dr. Munaim Tahir and Dr. Mubashr Ahmed. Valid, filed evidence.

A document only moves from the first status to the second when a human
updates it — never automatically, and never by this folder's mere presence.

## How this maps to the eventual Evidence app

When `backend/apps/evidence` is built (per the stage-gated build order in
`README.md` and `AGENTS.md` — this is *not* Stage 0 and should not be built
early), each `manifest.json` entry is intended to become one `EvidenceRecord`
per `indicator_id`:

- `payload` = the corresponding file
- `is_current` = `false` until an authenticated human approval action flips
  it to `true` — mirroring the signed status of the physical/digital document
- One-time indicators with multiple `indicator_ids` sharing a single document
  (e.g. ASL-SOP-12 covering indicators 68–73) create one `EvidenceRecord` per
  indicator, all pointing at the same file — per the locked decision that
  every indicator ID must appear in exactly one document, not that every
  indicator needs a physically distinct file.

Do not write the ingestion code until the stage that covers it is reached.
This README exists so that stage's build prompt has an unambiguous source
of truth for where the files and their metadata live.
