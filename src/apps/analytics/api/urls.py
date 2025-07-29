from rest_framework.routers import DefaultRouter

from apps.analytics.api.views import URLClickViewSet

app_name = 'analytics'

router = DefaultRouter()
router.register(r'url-clicks', URLClickViewSet, basename='url-clicks')

urlpatterns = [
    *router.urls
]