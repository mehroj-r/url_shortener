"""Gunicorn settings. Worker counts can be tuned per host with GUNICORN_WORKERS / GUNICORN_THREADS."""
import os

bind = '0.0.0.0:8000'
worker_class = 'gthread'
workers = int(os.environ.get('GUNICORN_WORKERS', 3))
threads = int(os.environ.get('GUNICORN_THREADS', 4))
timeout = 30
graceful_timeout = 30
# Recycle workers now and then to cap memory growth
max_requests = 1000
max_requests_jitter = 100
accesslog = '-'
