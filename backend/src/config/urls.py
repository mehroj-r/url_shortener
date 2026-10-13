import re

from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path

from apps.analytics.views import redirect_short_url
from apps.shortener.validators import RESERVED_SHORT_CODES, SHORT_CODE_PATTERN

# Reserved first segments without a trailing slash (e.g. "/admin") must not be
# treated as short codes, so CommonMiddleware can append the slash instead.
reserved_pattern = '|'.join(f'{re.escape(code)}/?$' for code in RESERVED_SHORT_CODES)
short_code_pattern = f'^(?!({reserved_pattern}))(?P<short_code>{SHORT_CODE_PATTERN})/?$'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.url_router', namespace='api-v1')),
    re_path(short_code_pattern, redirect_short_url, name='url-click'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    import debug_toolbar

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
        path("query-analyzer/", include("django_query_analyzer.urls")),
        *urlpatterns
    ]
