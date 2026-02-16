web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py setup_groups 2>/dev/null || true && gunicorn news_app.wsgi:application --bind 0.0.0.0:$PORT
