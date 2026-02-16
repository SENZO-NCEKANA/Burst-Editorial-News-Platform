#!/bin/sh
set -e

# Run migrations
python manage.py migrate --noinput

# Setup user groups (Reader, Journalist, Editor, Publisher)
python manage.py setup_groups 2>/dev/null || true

# Start the server
exec "$@"
