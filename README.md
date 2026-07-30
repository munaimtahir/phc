# PHC MSDS Compliance Tracker — Al Shifa Laboratory

Compliance tracking + AI drafting assistant for the Punjab Healthcare Commission's
Minimum Service Delivery Standards (MSDS), Clinical/Pathology Laboratories.

118 indicators · 37 standards · 10 domains. See `docs/data/indicators_master.json`
for the canonical, locked registry, and `AI_DEV_PACK.md` for the full design pack.

## Two sections

- **Section A — Compliance Tracker**: indicator registry, daily due-list for
  recurring evidence, compliance scoring, single-button print pack for PHC visits.
- **Section B — AI Drafting Assistant**: drafts SOPs/policies (one-time indicators)
  and reusable templates (recurring documentary indicators), grounded in each
  indicator's actual compliance requirements. Every draft requires human
  review/approval before it counts as filed evidence — no auto-publish.

## Build order (stage-gated — read `AGENTS.md` before touching code)

1. **Stage 0** — registry + Lab Profile, read-only. *(current stage — see the
   build prompt in `AI_DEV_PACK.md` §9)*
2. **Stage 1** — recurring entry + daily due-list + compliance scoring
3. **Stage 2** — print/export engine
4. **Section B** — AI drafting assistant (parallel track, starts once Stage 1 is stable)

## Stack

Django + DRF (backend) · React + Vite + TypeScript + Tailwind (frontend) ·
PostgreSQL · Redis · Docker Compose · Nginx.

This matches the stack used across your other builds (nexpat/ConsultCall/FMU SIMS/ClinicQ).
If AccrediOps at `phc.alshifalab.pk` already runs on something different, flag it —
this scaffold should match that rather than diverge.

## Repo layout

```
backend/          Django project — apps/registry, apps/evidence, apps/compliance,
                   apps/exports (Section A), apps/drafting (Section B)
frontend/          React + Vite + TS + Tailwind
docs/status/       Living development status doc (update as stages complete)
docs/decisions/    Locked decisions log (ADR-style, one file per decision batch)
docs/data/         indicators_master.json — canonical seed data, do not hand-edit
nginx/             Reverse proxy config for prod
```

## Getting started

```bash
git init
git add .
git commit -m "Scaffold: PHC MSDS Compliance Tracker"
git remote add origin <your-repo-url>
git push -u origin main
```

Then hand `AI_DEV_PACK.md` §9 (Stage 0 build prompt) to the coding agent working
in this repo.
