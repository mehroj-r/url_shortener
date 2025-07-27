from rest_framework_extensions.routers import ExtendedDefaultRouter

from apps.shortener.api.views import ShortURLViewSet, URLViewSet, URLCollectionViewSet, URLNestedViewSet, \
    ShortURLNestedViewSet

app_name = 'shortener'

router = ExtendedDefaultRouter()

# Base routers
collections_router = router.register(r'url-collections', URLCollectionViewSet, basename='url_collections')
urls_router = router.register(r'urls', URLViewSet, basename='urls')
short_urls_router = router.register(r'short-urls', ShortURLViewSet, basename='short_urls')

# Nested routers
urls_nested_router = collections_router.register(r'urls', URLNestedViewSet, basename='collection-urls', parents_query_lookups=['collection'])
short_urls_nested_router = urls_router.register(r'short-urls', ShortURLNestedViewSet, basename='short-urls', parents_query_lookups=['url'])

urlpatterns = [
    *router.urls
]