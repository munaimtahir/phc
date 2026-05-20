# Development Roadmap

## Phase 1 — Foundation
- Create Django project.
- Add apps: core, accounts, indicators, evidence, registers, reports.
- Configure settings, static/media, authentication, health endpoint.
- Add Docker and docker-compose.
- Add PostgreSQL production configuration.
- Add SQLite local testing support.
- Add base templates and Bootstrap UI.

Acceptance:
- `/health/` returns 200.
- Login/logout works.
- Dashboard page loads for authenticated user.
- Protected pages redirect unauthenticated users.

## Phase 2 — Indicator and Evidence Requirement Core
- Add Indicator model.
- Add EvidenceRequirement model.
- Add IndicatorCompliance snapshot/calculation support.
- Import 118 indicators.
- Bootstrap evidence requirements from CSV/manual seed.
- Add admin views.
- Add indicator list and detail pages.

Acceptance:
- 118 indicators are imported.
- Each indicator has at least one evidence requirement.
- Indicator detail shows requirement checklist.
- Indicator status can be calculated from requirement status.

## Phase 3 — Evidence Library
- Add EvidenceItem model.
- Add EvidenceRequirementFulfillment model.
- Build upload form.
- Build evidence list/detail.
- Link evidence to one or more requirements.
- Add approval/review fields.
- Add physical file reference and display location fields.

## Phase 4 — Registers
- Add RegisterDefinition.
- Add RegisterEntry.
- Add recurrence logic.
- Add register list/detail/entry pages.
- Auto-create evidence from register entries.
- Add printable register view.

## Phase 5 — Dashboard and Reports
- Dashboard KPI cards.
- Functional area summary.
- Standard-wise progress.
- Missing evidence panel.
- Overdue register panel.
- Recent updates panel.
- Score summary report.
- Missing evidence report.
- Evidence index.
- Recurring compliance report.
- Surveyor pack index.

## Phase 6 — AI Prompt Generator
- Create prompt generator service.
- Generate prompts per evidence requirement.
- Add prompt type buttons.
- Add copy button.
- Add download `.txt`.
- Ensure no live AI API calls.
- Include approval/signature instructions.

## Phase 7 — Deployment and Polish
- Docker build.
- Caddy reverse proxy.
- Static/media persistence.
- Backup instructions.
- Print CSS.
- Final QA gates.
- Basic admin training guide.
