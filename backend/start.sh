#!/bin/bash

# Start Celery worker in background
python -m celery -A celery_app.celery worker --loglevel=info --concurrency=1 &

# Start Celery beat scheduler in background  
python -m celery -A celery_app.celery beat --loglevel=info &

# Start Flask with gunicorn (foreground - keeps container alive)
gunicorn wsgi:app --bind 0.0.0.0:$PORT