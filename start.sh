#!/usr/bin/env bash
set -o errexit

python manage.py migrate --no-input

if [ "$DJANGO_SEED_DATA" = "True" ]; then
  python manage.py seed_data
fi

gunicorn soghlom_turmush.wsgi:application --bind 0.0.0.0:${PORT:-8000}
