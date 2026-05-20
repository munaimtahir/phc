# Setup.md

## Target Path
`/home/munaim/srv/apps/phc`

## Basic Setup
```bash
mkdir -p /home/munaim/srv/apps/phc
cd /home/munaim/srv/apps/phc
git init
python3 -m venv venv
source venv/bin/activate
pip install Django gunicorn psycopg[binary] dj-database-url python-decouple whitenoise django-htmx weasyprint pytest pytest-django ruff
django-admin startproject config .
python manage.py startapp core
python manage.py startapp accounts
python manage.py startapp indicators
python manage.py startapp evidence
python manage.py startapp registers
python manage.py startapp reports
```

## Caddy
```caddy
phc.alshifalab.pk {
    encode zstd gzip
    reverse_proxy 127.0.0.1:8018
}
```
