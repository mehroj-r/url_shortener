from rest_framework.throttling import ScopedRateThrottle

from core.utils.request import get_client_ip


class ClientIPScopedRateThrottle(ScopedRateThrottle):
    """
    Scoped throttle keyed on the IP from `get_client_ip`.

    DRF's default identifier trusts the client-supplied X-Forwarded-For header,
    which lets anyone bypass the limit by changing it on every request.
    """

    def get_ident(self, request):
        return get_client_ip(request)
