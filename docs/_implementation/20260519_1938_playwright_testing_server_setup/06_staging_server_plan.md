# Staging/Server Execution Plan

## GitHub Actions Mode (documented plan)
Use a workflow that:
- checks out code
- installs node deps
- installs Playwright chromium
- sets `PLAYWRIGHT_BASE_URL` to staged deployment URL
- injects `PLAYWRIGHT_USERNAME`/`PLAYWRIGHT_PASSWORD` from secrets
- runs smoke + layout on push/manual dispatch
- uploads `playwright-report/` and `test-results/` artifacts

Minimal workflow steps:
- `npm ci`
- `npx playwright install chromium`
- `npm run test:e2e:smoke`
- `npm run test:e2e:layout`
- `actions/upload-artifact`

## VPS/Staging Mode
- Run against staging URL only.
- Suggested command script:
  - export env vars
  - run `npm run test:e2e:smoke`
  - run `npm run test:e2e:layout`
  - run `npm run test:e2e`
- Schedule via cron (e.g., nightly) or run manually pre-release.
- Store reports under:
  - `playwright-report/`
  - `test-results/`
  - optionally copy snapshots to `docs/_verification/` for audit trail.

## Mutation Safety
- Keep `PLAYWRIGHT_ALLOW_MUTATION=false` by default.
- Enable only on test/staging datasets with explicit approval.
