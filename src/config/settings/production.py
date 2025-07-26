from .base import *

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://1e14f8056d9bf68437d9120993354598@o4509733155831808.ingest.de.sentry.io/4509733158125648",
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