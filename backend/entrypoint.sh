#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py load_indicators
python manage.py seed_admin

exec python manage.py runserver 0.0.0.0:8000
