def get_client_ip(request) -> str | None:
    """
    Return the client IP address.

    In production the app is only reachable through nginx, which overwrites
    X-Real-IP with the resolved client address, so the header can be trusted.
    """
    return request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR') or None
