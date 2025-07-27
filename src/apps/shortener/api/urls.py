from rest_framework import routers
from rest_framework.routers import DefaultRouter

from apps.shortener.api.views import ShortURLViewSet, URLViewSet, URLCollectionViewSet

app_name = 'shortener'

router = DefaultRouter()
router.register('urls', URLViewSet, basename='urls')
router.register('url-collections', URLCollectionViewSet, basename='url_collections')
router.register('short-urls', ShortURLViewSet, basename='short_urls')

urlpatterns = [
    *router.urls
]