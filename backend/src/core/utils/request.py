import ipaddress
from functools import cache

from django.conf import settings


@cache
def _networks(cidrs: tuple[str, ...]):
    return tuple(ipaddress.ip_network(cidr) for cidr in cidrs)


def _parse(value: str):
    try:
        return ipaddress.ip_address(value.strip())
    except ValueError:
        return None


def _is_trusted(address) -> bool:
    return any(address in network for network in _networks(tuple(settings.TRUSTED_PROXY_NETWORKS)))


def get_client_ip(request) -> str | None:
    """
    Return the client IP address.

    In production the app is reached through the host's reverse proxy, which appends
    the address it saw to X-Forwarded-For. Walking that header from the right and
    skipping trusted proxy addresses (TRUSTED_PROXY_NETWORKS) finds the first address
    no trusted proxy vouches for, so a client can't choose its own IP by sending the
    header itself. A request that doesn't come from a trusted proxy is taken at face value.
    """
    remote = _parse(request.META.get('REMOTE_ADDR') or '')
    if remote is None:
        return None
    if not _is_trusted(remote):
        return str(remote)

    forwarded = [part for part in request.META.get('HTTP_X_FORWARDED_FOR', '').split(',') if part.strip()]
    for part in reversed(forwarded):
        address = _parse(part)
        if address is None:
            return None
        if not _is_trusted(address):
            return str(address)
    # Every hop is a trusted address (e.g. a client on the private network)
    first = _parse(forwarded[0]) if forwarded else remote
    return str(first) if first else None
