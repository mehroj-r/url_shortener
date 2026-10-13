import ipaddress
import logging

from django.conf import settings
from django.db import DatabaseError
from django.shortcuts import redirect
from django.views.decorators.http import require_safe

from apps.analytics.models import URLClick
from apps.shortener.models import ShortURL
from core.utils.request import get_client_ip

logger = logging.getLogger(__name__)

USER_AGENT_MAX_LENGTH = URLClick._meta.get_field('user_agent').max_length
REFERER_MAX_LENGTH = URLClick._meta.get_field('referer').max_length


@require_safe
def redirect_short_url(request, short_code):
    short_url = (
        ShortURL.objects
        .select_related('url')
        .filter(short_url=short_code, is_active=True, url__deleted_at__isnull=True)
        .first()
    )

    if short_url is None:
        return redirect(settings.DEFAULT_REDIRECT_URL)

    # HEAD requests come from link checkers, not visitors
    if request.method == 'GET':
        record_click(request, short_url)

    return redirect(short_url.url.url)


def record_click(request, short_url):
    """Store the click. A failure here is logged but never blocks the redirect."""
    ip = get_client_ip(request)
    try:
        ip_version = ipaddress.ip_address(ip).version if ip else None
    except ValueError:
        ip_version = None

    try:
        URLClick.objects.create(
            short_url=short_url,
            ipv4_address=ip if ip_version == 4 else None,
            ipv6_address=ip if ip_version == 6 else None,
            user_agent=request.headers.get('User-Agent', '')[:USER_AGENT_MAX_LENGTH] or None,
            referer=request.headers.get('Referer', '')[:REFERER_MAX_LENGTH] or None,
        )
    except DatabaseError:
        logger.exception('Failed to record a click for short URL %s', short_url.pk)
