#!/usr/bin/env bash
set -e

# Apply DB migrations
python manage.py migrate --noinput

# Create a default superuser if DJANGO_SUPERUSER_EMAIL is set and user doesn't exist
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  echo "from django.contrib.auth import get_user_model; User = get_user_model();
import sys
if not User.objects.filter(email=\"$DJANGO_SUPERUSER_EMAIL\").exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME','$DJANGO_SUPERUSER_EMAIL','$DJANGO_SUPERUSER_PASSWORD')
" | python manage.py shell || true
fi

# Collect static (no-op if not configured)
python manage.py collectstatic --noinput || true

# Start server via gunicorn
exec "$@"
