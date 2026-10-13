from .base import *

import sentry_sdk
from sentry_sdk.scrubber import DEFAULT_DENYLIST, EventScrubber

SECRET_KEY = config('SECRET_KEY')

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=60 * 60 * 24 * 365, cast=int)
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'


sentry_sdk.init(
    dsn=config('SENTRY_DSN', default=''),
    traces_sample_rate=config('SENTRY_TRACES_SAMPLE_RATE', default=0.1, cast=float),
    send_default_pii=False,
    event_scrubber=EventScrubber(
        denylist=DEFAULT_DENYLIST + ['password_repeat', 'refresh', 'access'],
        recursive=True,
    ),
    release=f'url_shortener@{APP_VERSION}',
    environment='production',
)
