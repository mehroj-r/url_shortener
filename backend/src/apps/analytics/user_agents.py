import re
from dataclasses import dataclass
from functools import lru_cache
from urllib.parse import urlsplit

from ua_parser import parse

# Fetchers that ua-parser doesn't flag as spiders but never belong to a human visit
EXTRA_BOTS = re.compile(r'HeadlessChrome|python-requests|python-httpx|curl/|Wget/|Go-http-client|okhttp', re.I)
DESKTOP_OS = {'Windows', 'Mac OS X', 'Linux', 'Ubuntu', 'Fedora', 'Chrome OS', 'FreeBSD'}
MOBILE_OS = {'iOS', 'Android', 'HarmonyOS', 'KaiOS'}


@dataclass(frozen=True)
class ClientInfo:
    browser: str = ''
    os: str = ''
    device: str = 'other'
    is_bot: bool = False


@lru_cache(maxsize=2048)
def parse_user_agent(user_agent: str) -> ClientInfo:
    """Classify a User-Agent into browser, OS, device type, and whether it is a bot (e.g. a link preview)."""
    if not user_agent:
        return ClientInfo()

    result = parse(user_agent)
    browser = result.user_agent.family if result.user_agent else ''
    os = result.os.family if result.os else ''
    device_family = result.device.family if result.device else ''

    if device_family == 'Spider' or EXTRA_BOTS.search(user_agent):
        return ClientInfo(browser=browser, os=os, device='bot', is_bot=True)

    if 'iPad' in device_family or 'Tablet' in user_agent or (os == 'Android' and 'Mobile' not in user_agent):
        device = 'tablet'
    elif os in MOBILE_OS or 'Mobile' in user_agent:
        device = 'mobile'
    elif os in DESKTOP_OS:
        device = 'desktop'
    else:
        device = 'other'

    # "Mobile Safari" and "Chrome Mobile" are the same browsers to a link owner
    browser = browser.removeprefix('Mobile ').removesuffix(' Mobile')
    return ClientInfo(browser=browser, os=os.replace('Mac OS X', 'macOS'), device=device)


def referer_domain(referer: str | None) -> str | None:
    """Return the referring host without "www.", or None for direct visits."""
    if not referer:
        return None
    host = urlsplit(referer).hostname
    return host.removeprefix('www.') if host else None
