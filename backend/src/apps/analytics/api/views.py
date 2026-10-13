from rest_framework import viewsets
from django_filters import rest_framework as filters
from apps.analytics.api.filters import URLClickFilterSet
from apps.analytics.api.serializers import URLClickSerializer
from apps.analytics.models import URLClick
from core.api.views import BaseAPIViewSet


class URLClickViewSet(BaseAPIViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = URLClick.objects.order_by('-created_at')
    serializer_class = URLClickSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = URLClickFilterSet
    user_field = 'short_url__url__user'
