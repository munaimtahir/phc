# Commands Run

```bash
# context / credential detection
date -u +%Y%m%d_%H%M
if [ -n "$PLAYWRIGHT_USERNAME" ]; then echo "PW_USER_SET=1"; else echo "PW_USER_SET=0"; fi
if [ -n "$PLAYWRIGHT_PASSWORD" ]; then echo "PW_PASS_SET=1"; else echo "PW_PASS_SET=0"; fi

# required env for this run
export PLAYWRIGHT_BASE_URL="https://phc.alshifalab.pk"
export PLAYWRIGHT_ALLOW_MUTATION="false"

# verification commands
./venv/bin/python manage.py check
npm run test:e2e:smoke
npm run test:e2e:layout
npm run test:e2e
```
