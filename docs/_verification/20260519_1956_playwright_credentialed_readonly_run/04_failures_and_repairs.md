# Failures and Repairs

## Failure 1: Protected-route execution blocked
- Symptom: smoke/layout/protected workflow tests were skipped.
- Root cause: environment credentials were not set (`PLAYWRIGHT_USERNAME`, `PLAYWRIGHT_PASSWORD`).
- Changed file: none (application code unchanged).
- Repair summary: not applicable in code; requires runtime environment credential injection.

## Application defects repaired in this run
- None (no protected-route execution occurred, so no runtime defects were observed to fix).
