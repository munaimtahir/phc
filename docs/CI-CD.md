# CI-CD.md

## Local Gates
```bash
python manage.py check
python manage.py makemigrations --check --dry-run
pytest
ruff check .
```

## Docker Gates
```bash
docker compose build
docker compose up -d
docker compose ps
curl -I http://127.0.0.1:8018/health/
```

## Public Check
```bash
curl -I https://phc.alshifalab.pk/health/
```
