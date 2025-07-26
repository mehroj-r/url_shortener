from .base import *

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