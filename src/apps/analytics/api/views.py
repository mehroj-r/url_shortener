from django.conf import settings
from django.shortcuts import redirect
from rest_framework import viewsets
from django_filters import rest_framework as filters
from apps.analytics.api.filters import URLClickFilterSet
from apps.analytics.api.serializers import URLClickSerializer
from apps.analytics.models import URLClick
from apps.shortener.models import ShortURL
from core.api.views import BaseAPIView


class URLClickView(BaseAPIView):
    serializer_class = URLClickSerializer
    permission_classes = []
    authentication_classes = []
    user_field = None

    def get(self, request, *args, **kwargs):

        path = request.path.strip('/')
        remote_addr = request._request.META.get('HTTP_X_REAL_IP', None)
        user_agent = request._request.META.get('HTTP_USER_AGENT', None)
        referer = request._request.META.get('HTTP_X_REFERER', None)

        try:
            short_url = ShortURL.objects.get(short_url=path)
        except ShortURL.DoesNotExist:
            return redirect(settings.DEFAULT_REDIRECT_URL)

        data = {
            'short_url': short_url.id,
            'ipv4_address': remote_addr,
            'ipv6_address': None,
            'user_agent': user_agent,
            'referer': referer
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return redirect(short_url.url.url)

    def finalize_response(self, request, response, *args, **kwargs):
        return response


class URLClickViewSet(BaseAPIView, viewsets.ReadOnlyModelViewSet):
    queryset = URLClick.objects.all()
    serializer_class = URLClickSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = URLClickFilterSet
    user_field = None