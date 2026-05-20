# Test Commands

## Setup
```bash
npm install
npx playwright install chromium
```

## Environment
```bash
export PLAYWRIGHT_BASE_URL="http://127.0.0.1:8018"
export PLAYWRIGHT_USERNAME="<test-user>"
export PLAYWRIGHT_PASSWORD="<test-password>"
export PLAYWRIGHT_ALLOW_MUTATION="false"
```

## E2E Commands
```bash
npm run test:e2e
npm run test:e2e:smoke
npm run test:e2e:layout
npm run test:e2e:headed
npm run test:e2e:ui
npm run test:e2e:report
```

## Mutation Mode (safe staging only)
```bash
export PLAYWRIGHT_ALLOW_MUTATION="true"
npm run test:e2e -- tests/e2e/evidence.spec.ts tests/e2e/registers.spec.ts
```

## Django Sanity
```bash
./venv/bin/python manage.py check
```
