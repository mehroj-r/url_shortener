from .base import *

# Local development only; production reads SECRET_KEY from the environment.
SECRET_KEY = SECRET_KEY or 'django-insecure-local-development-only'

INSTALLED_APPS += [
    'debug_toolbar',
    'django_extensions',
    'django_query_analyzer',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_query_analyzer.middleware.QueryAnalyzerMiddleware'
]

# Debug Toolbar
INTERNAL_IPS = [
    '127.0.0.1',
]
