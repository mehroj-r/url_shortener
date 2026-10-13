from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from apps.shortener.api.views import ShortURLViewSet, URLViewSet, URLCollectionViewSet, URLNestedViewSet, \
    ShortURLNestedViewSet, TagViewSet

app_name = 'shortener'

router = DefaultRouter()

# Base routers
router.register(r'url-collections', URLCollectionViewSet, basename='url_collections')
router.register(r'urls', URLViewSet, basename='urls')
router.register(r'short-urls', ShortURLViewSet, basename='short_urls')
router.register(r'tags', TagViewSet, basename='tags')

# Nested routers
collections_router = NestedSimpleRouter(router, r'url-collections', lookup='collection')
collections_router.register(r'urls', URLNestedViewSet, basename='collection-urls')

urls_router = NestedSimpleRouter(router, r'urls', lookup='url')
urls_router.register(r'short-urls', ShortURLNestedViewSet, basename='short-urls')

urlpatterns = [
    *router.urls,
    *collections_router.urls,
    *urls_router.urls,
]
