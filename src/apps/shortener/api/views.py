from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.shortener.api.serializers import URLSerializer, URLCollectionSerializer, ShortURLSerializer
from apps.shortener.models import URL, URLCollection, ShortURL
from core.api.views import BaseAPIView


class URLViewSet(BaseAPIView, viewsets.ModelViewSet):
    queryset = URL.objects.all()
    serializer_class = URLSerializer
    permission_classes = [IsAuthenticated]


class URLCollectionViewSet(BaseAPIView, viewsets.ModelViewSet):
    queryset = URLCollection.objects.all()
    serializer_class = URLCollectionSerializer
    permission_classes = [IsAuthenticated]


class ShortURLViewSet(BaseAPIView, viewsets.ModelViewSet):
    queryset = ShortURL.objects.all()
    serializer_class = ShortURLSerializer
    permission_classes = [IsAuthenticated]