from .base import *

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 86400
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'


sentry_sdk.init(
    dsn=config('SENTRY_DSN', default=''),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    sample_rate=1.0,
    max_breadcrumbs=100,
    max_value_length=1024,
    send_default_pii=True,
    attach_stacktrace=True,
    include_source_context=False,
    include_local_variables=True,
    send_client_reports=True,
    max_request_body_size="always",
    release="url_shortener@1.0.0",
    environment="production",
)