# 0001 — Locked Decisions (Pre-Stage-0)

Status: Locked. See `AI_DEV_PACK.md` for full reasoning behind each.

| # | Decision | Value |
|---|---|---|
| 1 | Indicator taxonomy | physical / one_time / recurring |
| 2 | One-time indicators | latest version only retained, revised every 2–3 yrs |
| 3 | Recurring evidence retention | ~1 year, configurable |
| 4 | Auth (MVP) | single shared login, 2–3 staff |
| 5 | Recurring evidence status | fully_met / partially_met / not_met captured per entry |
| 6 | Daily indicator schedule | lab operates 7 days/week |
| 7 | On-time/late tracking | none — due-list is presence-only, no deadline logic |
| 8 | Print pack ordering | mirrors PHC's own domain → standard → indicator numbering |
| 9 | Evidence format | mixed per indicator — photo / document / structured_form (see registry) |
| 10 | Lab Profile | locked as a foundational object — see seed values below |
| 11 | Section B scope | one-time/policy indicators + templates for recurring documentary indicators (not physical) |
| 12 | Section B trigger | on-demand (single indicator) and bulk generation both supported |
| 13 | Section B publishing | draft → human review/approval required before becoming filed evidence; never automatic |

## Lab Profile seed values

- lab_name: Al Shifa Laboratory
- address: Circular Road, Jaranwala
- phc_registration_no: P-20787
- supervising_pathologist: Dr. Mubashr Ahmed

## Indicator classification provenance

`docs/data/indicators_master.json` — 102 indicators via rule-based classification
(accepted as-is), 16 via manual override where no rule matched confidently.
Each manually-classified record carries `classification_source: manual_override`
and a `classification_note` explaining the call. See `AI_DEV_PACK.md` §4.

## Adding new decisions

Append a new `000N-*.md` file per future decision batch rather than editing this
one — keep the history, don't overwrite it.
