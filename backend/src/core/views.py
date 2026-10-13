from django.conf import settings
from django.http import Http404, HttpResponse
from django.utils.csp import CSP
from django.views.decorators.csp import csp_override
from django.views.decorators.http import require_safe

# The web app loads only its own scripts, styles, fonts and API; React sets inline styles.
WEB_APP_CSP = {
    'default-src': [CSP.SELF],
    'script-src': [CSP.SELF],
    'style-src': [CSP.SELF, CSP.UNSAFE_INLINE],
    'img-src': [CSP.SELF, 'data:', 'blob:'],
    'font-src': [CSP.SELF],
    'connect-src': [CSP.SELF],
    'frame-ancestors': [CSP.NONE],
    'base-uri': [CSP.SELF],
    'form-action': [CSP.SELF],
}


@csp_override(WEB_APP_CSP)
@require_safe
def web_app(request, path=''):
    """The web app's page for every route under /app/; the browser-side router takes it from there."""
    try:
        html = (settings.FRONTEND_DIR / 'index.html').read_bytes()
    except FileNotFoundError:
        raise Http404('The web app has not been built.') from None
    response = HttpResponse(html, content_type='text/html; charset=utf-8')
    # Always revalidate, so a deploy is picked up on the next visit
    response['Cache-Control'] = 'no-cache'
    return response
