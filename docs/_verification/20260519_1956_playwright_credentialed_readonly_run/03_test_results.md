# Test Results

## Summary
- Django check: PASS
- Smoke suite: 0 passed, 0 failed, 1 skipped
- Layout suite: 0 passed, 0 failed, 3 skipped
- Full E2E suite: 1 passed, 0 failed, 13 skipped

## Passed tests
- `Authentication flow › login page opens`

## Skipped tests
- All protected-route tests skipped due to missing `PLAYWRIGHT_USERNAME` and `PLAYWRIGHT_PASSWORD`.
- Mutation tests also skipped because `PLAYWRIGHT_ALLOW_MUTATION=false`.

## Failed test names
- None

## Artifacts
- HTML report: `playwright-report/`
- Raw results: `test-results/`
- No failure screenshots/traces generated in this run because no tests failed.
