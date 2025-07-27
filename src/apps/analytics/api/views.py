from django.shortcuts import redirect

from apps.analytics.api.serializers import URLClickSerializer
from apps.shortener.models import URL, ShortURL
from core.api.views import BaseAPIView

class URLClickView(BaseAPIView):
    serializer_class = URLClickSerializer
    permission_classes = []
    authentication_classes = []

    def get(self, request, *args, **kwargs):

        path = request.path.strip('/')
        remote_addr = request._request.META.get('HTTP_X_REAL_IP', None)
        remote_addr2 = request._request.META.get('REMOTE_ADDR', None)
        user_agent = request._request.META.get('HTTP_USER_AGENT', None)
        referer = request._request.META.get('HTTP_REFERER', None)

        short_url = ShortURL.objects.get(short_url=path)

        data = {
            'url': short_url.id,
            'ipv4_address': remote_addr or remote_addr2,
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
