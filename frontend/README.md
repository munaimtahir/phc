# Frontend (React + Vite + TypeScript + Tailwind)

Not yet a real Vite project — placeholder layout for Stage 0 to scaffold
properly (`npm create vite@latest . -- --template react-ts`, then add
Tailwind). Don't hand-write `vite.config.ts`/`tsconfig.json`; generate them.

## Intended page boundaries

- `src/pages/registry/` — Stage 0. Read-only indicator registry, filterable.
- `src/pages/daily/` — Stage 1. Daily due-list, recurring evidence entry form.
- `src/pages/print/` — Stage 2. Print pack trigger + preview.
- `src/pages/drafting/` — Section B. Draft generation UI, review/approve screen.
- `src/lib/api.ts` — single place for API base URL + fetch wrappers, so the
  backend URL only needs changing in one spot.
