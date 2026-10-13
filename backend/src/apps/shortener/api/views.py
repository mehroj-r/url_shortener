from django.db.models import Count, Max, Prefetch, Q
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_nested.viewsets import NestedViewSetMixin

from apps.shortener.api.filters import URLFilterSet
from apps.shortener.api.serializers import (
    BulkLinkActionSerializer,
    URLSerializer,
    URLCollectionSerializer,
    ShortURLSerializer,
    TagSerializer,
    URLNestedSerializer, ShortURLNestedSerializer
)
from apps.shortener.models import URL, URLCollection, ShortURL, Tag
from core.api.views import BaseAPIViewSet

# Human clicks only: link previews and crawlers are recorded but not counted
COUNTED_CLICKS = Q(clicks__deleted_at__isnull=True, clicks__is_bot=False)
LINK_CLICKS = Q(short_urls__clicks__deleted_at__isnull=True, short_urls__clicks__is_bot=False)


def annotated_short_urls():
    return ShortURL.objects.annotate(click_count=Count('clicks', filter=COUNTED_CLICKS))


def annotated_links():
    return (
        URL.objects
        .select_related('collection')
        .prefetch_related(Prefetch('short_urls', queryset=annotated_short_urls().order_by('created_at')), 'tags')
        .annotate(
            clicks=Count('short_urls__clicks', filter=LINK_CLICKS, distinct=True),
            last_clicked_at=Max('short_urls__clicks__created_at', filter=LINK_CLICKS),
        )
    )


class URLViewSet(BaseAPIViewSet, viewsets.ModelViewSet):
    queryset = annotated_links().order_by('-created_at')
    serializer_class = URLSerializer
    permission_classes = [IsAuthenticated]
    user_field = 'user'
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = URLFilterSet
    search_fields = ['name', 'url', 'short_urls__short_url']
    ordering_fields = ['created_at', 'name', 'clicks', 'last_clicked_at']

    @action(detail=False, methods=['post'])
    def bulk(self, request):
        """Apply one action to many links at once."""
        serializer = BulkLinkActionSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        links = URL.objects.filter(user=request.user, pk__in=data['ids'])
        count = links.count()
        match data['action']:
            case 'delete':
                links.delete()
            case 'move':
                links.update(collection=data['collection'])
            case 'add_tag':
                data['tag'].urls.add(*links)
            case 'remove_tag':
                data['tag'].urls.remove(*links)
            case 'activate' | 'deactivate':
                ShortURL.objects.filter(url__in=links).update(is_active=data['action'] == 'activate')
        return Response({'count': count})


class URLCollectionViewSet(BaseAPIViewSet, viewsets.ModelViewSet):
    queryset = URLCollection.objects.annotate(
        link_count=Count('urls', filter=Q(urls__deleted_at__isnull=True), distinct=True),
        clicks=Count(
            'urls__short_urls__clicks',
            filter=Q(urls__deleted_at__isnull=True, urls__short_urls__clicks__deleted_at__isnull=True,
                     urls__short_urls__clicks__is_bot=False),
            distinct=True,
        ),
    ).order_by('name')
    serializer_class = URLCollectionSerializer
    permission_classes = [IsAuthenticated]
    user_field = 'user'

    def perform_destroy(self, instance):
        # Links leave the collection instead of being deleted with it, unless asked
        if self.request.query_params.get('delete_links') not in ('1', 'true'):
            instance.urls.update(collection=None)
        instance.delete()


class TagViewSet(BaseAPIViewSet, viewsets.ModelViewSet):
    queryset = Tag.objects.annotate(
        link_count=Count('urls', filter=Q(urls__deleted_at__isnull=True)),
    ).order_by('name')
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    user_field = 'user'


class ShortURLViewSet(BaseAPIViewSet, viewsets.ModelViewSet):
    queryset = annotated_short_urls().order_by('-created_at')
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
