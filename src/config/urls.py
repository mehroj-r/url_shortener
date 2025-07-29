from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from apps.analytics.api.views import URLClickView

app_name = 'config'

# Define reserved paths
RESERVED_PATHS = ['admin', 'api', 'static', 'media']

# Create the regex pattern dynamically
reserved_pattern = '|'.join([f'{path}/?$' for path in RESERVED_PATHS])
url_click_pattern = f'^(?!({reserved_pattern}))[a-zA-Z0-9]+/?$'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.url_router', namespace='api-v1')),
    re_path(url_click_pattern, URLClickView.as_view(), name='url-click'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
        path("query-analyzer/", include("django_query_analyzer.urls")),
        *urlpatterns
    ]