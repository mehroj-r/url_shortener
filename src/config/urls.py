from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from apps.analytics.api.views import URLClickView

app_name = 'config'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.url_router', namespace='api-v1')),
    re_path(r'^[a-zA-Z0-9]+$', URLClickView.as_view(), name='url-click'),
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