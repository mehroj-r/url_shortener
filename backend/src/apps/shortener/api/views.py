from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_nested.viewsets import NestedViewSetMixin

from apps.shortener.api.serializers import (
    URLSerializer,
    URLCollectionSerializer,
    ShortURLSerializer,
    URLNestedSerializer, ShortURLNestedSerializer
)
from apps.shortener.models import URL, URLCollection, ShortURL
from core.api.views import BaseAPIViewSet


class URLViewSet(BaseAPIViewSet, viewsets.ModelViewSet):
    queryset = URL.objects.select_related('collection').order_by('-created_at')
    serializer_class = URLSerializer
    permission_classes = [IsAuthenticated]
    user_field = 'user'


class URLCollectionViewSet(BaseAPIViewSet, viewsets.ModelViewSet):
    queryset = URLCollection.objects.order_by('-created_at')
    serializer_class = URLCollectionSerializer
    permission_classes = [IsAuthenticated]
    user_field = 'user'


class ShortURLViewSet(BaseAPIViewSet, viewsets.ModelViewSet):
    queryset = ShortURL.objects.order_by('-created_at')
    serializer_class = ShortURLSerializer
    permission_classes = [IsAuthenticated]
    user_field = 'url__user'


class URLNestedViewSet(NestedViewSetMixin, URLViewSet):
    serializer_class = URLNestedSerializer
    parent_lookup_kwargs = {'collection_pk': 'collection__pk'}

    def perform_create(self, serializer):
        collection = get_object_or_404(URLCollection, pk=self.kwargs['collection_pk'], user=self.request.user)
        serializer.save(collection=collection)


class ShortURLNestedViewSet(NestedViewSetMixin, ShortURLViewSet):
    serializer_class = ShortURLNestedSerializer
    parent_lookup_kwargs = {'url_pk': 'url__pk'}

    def perform_create(self, serializer):
        url = get_object_or_404(URL, pk=self.kwargs['url_pk'], user=self.request.user)
        serializer.save(url=url)
