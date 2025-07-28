from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_extensions.mixins import NestedViewSetMixin

from apps.shortener.api.serializers import (
    URLSerializer,
    URLCollectionSerializer,
    ShortURLSerializer,
    URLNestedSerializer, ShortURLNestedSerializer
)
from apps.shortener.models import URL, URLCollection, ShortURL
from core.api.views import BaseAPIView


class URLViewSet(BaseAPIView, viewsets.ModelViewSet):
    queryset = URL.objects.all()
    serializer_class = URLSerializer
    permission_classes = [IsAuthenticated]
    user_field = 'user'


class URLCollectionViewSet(BaseAPIView, viewsets.ModelViewSet):
    queryset = URLCollection.objects.all()
    serializer_class = URLCollectionSerializer
    permission_classes = [IsAuthenticated]
    user_field = 'user'


class ShortURLViewSet(BaseAPIView, viewsets.ModelViewSet):
    queryset = ShortURL.objects.all()
    serializer_class = ShortURLSerializer
    permission_classes = [IsAuthenticated]
    user_field = 'url__user'


class URLNestedViewSet(NestedViewSetMixin, URLViewSet):
    serializer_class = URLNestedSerializer


class ShortURLNestedViewSet(NestedViewSetMixin, ShortURLViewSet):
    serializer_class = ShortURLNestedSerializer