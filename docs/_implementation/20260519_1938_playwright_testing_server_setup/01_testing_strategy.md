# Playwright Testing Strategy

## Scope
PHC Lab Compliance Tracker practical E2E checks for:
- runtime/template failures
- login/session behavior
- route and workflow health
- desktop layout overlap issues
- indicator/evidence/register/report workflows

Product scope remains fixed to the single PHC checklist workflow.

## Safety Controls
Environment variables used:
- `PLAYWRIGHT_BASE_URL` (default `http://127.0.0.1:8018`)
- `PLAYWRIGHT_USERNAME`
- `PLAYWRIGHT_PASSWORD`
- `PLAYWRIGHT_ALLOW_MUTATION` (default false)

Rules implemented:
- read-only suites can run without mutation flag.
- mutation tests in evidence/register specs are skipped unless `PLAYWRIGHT_ALLOW_MUTATION=true`.
- no hardcoded credentials.

## Diagnostics
- screenshots on failure
- video retained on failure
- trace on first retry
- HTML report at `playwright-report/`
- raw artifacts under `test-results/`
