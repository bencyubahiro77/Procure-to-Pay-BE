#!/usr/bin/env bash
set -e

echo "Waiting for database..."
# Optional: Add a simple wait for postgres
sleep 2

echo "Running migrations..."
python manage.py migrate --noinput

# Create a default superuser if DJANGO_SUPERUSER_EMAIL is set and user doesn't exist
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  echo "Checking for superuser..."
  echo "from django.contrib.auth import get_user_model; User = get_user_model();
import sys
if not User.objects.filter(email=\"$DJANGO_SUPERUSER_EMAIL\").exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME','$DJANGO_SUPERUSER_EMAIL','$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created')
else:
    print('Superuser already exists')
" | python manage.py shell || true
fi

# Collect static files (remove || true so errors are caught)
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"
