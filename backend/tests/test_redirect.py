import pytest
from django.db import DatabaseError

from apps.analytics.models import URLClick
from apps.shortener.models import ShortURL

DEFAULT_REDIRECT_URL = 'https://default.example/'


@pytest.fixture(autouse=True)
def _default_redirect(settings):
    settings.DEFAULT_REDIRECT_URL = DEFAULT_REDIRECT_URL


@pytest.fixture
def short_url(alice, make_short_url):
    return make_short_url(alice, code='abc123', target='https://example.com/page')


@pytest.mark.django_db
class TestRedirect:

    def test_redirects_and_records_click(self, client, short_url):
        response = client.get(
            '/abc123',
            HTTP_X_FORWARDED_FOR='203.0.113.9',
            HTTP_REFERER='https://t.me/channel',
            HTTP_USER_AGENT='Firefox',
        )

        assert response.status_code == 302
        assert response['Location'] == 'https://example.com/page'
        click = URLClick.objects.get()
        assert click.short_url == short_url
        assert click.ipv4_address == '203.0.113.9'
        assert click.ipv6_address is None
        assert click.referer == 'https://t.me/channel'
        assert click.user_agent == 'Firefox'

    def test_trailing_slash_is_accepted(self, client, short_url):
        assert client.get('/abc123/')['Location'] == 'https://example.com/page'

    def test_ipv6_client(self, client, short_url):
        response = client.get('/abc123', HTTP_X_FORWARDED_FOR='2001:db8::1')

        assert response.status_code == 302
        click = URLClick.objects.get()
        assert (click.ipv4_address, click.ipv6_address) == (None, '2001:db8::1')

    def test_long_headers_are_truncated(self, client, short_url):
        response = client.get('/abc123', HTTP_USER_AGENT='u' * 1000, HTTP_REFERER='https://r.example/' + 'r' * 3000)

        assert response.status_code == 302
        click = URLClick.objects.get()
        assert len(click.user_agent) == 512
        assert len(click.referer) == 2048

    def test_missing_headers(self, client, short_url):
        response = client.get('/abc123', REMOTE_ADDR='')

        assert response.status_code == 302
        click = URLClick.objects.get()
        assert (click.ipv4_address, click.ipv6_address, click.user_agent, click.referer) == (None, None, None, None)

    def test_click_storage_failure_does_not_block_redirect(self, client, short_url, monkeypatch):
        def fail(*args, **kwargs):
            raise DatabaseError('disk full')

        monkeypatch.setattr(URLClick.objects, 'create', fail)

        response = client.get('/abc123')

        assert response.status_code == 302
        assert response['Location'] == 'https://example.com/page'

    def test_unknown_code_goes_to_default(self, client, db):
        response = client.get('/nope')

        assert response.status_code == 302
        assert response['Location'] == DEFAULT_REDIRECT_URL

    def test_inactive_code_goes_to_default(self, client, short_url):
        ShortURL.objects.filter(pk=short_url.pk).update(is_active=False)

        assert client.get('/abc123')['Location'] == DEFAULT_REDIRECT_URL
        assert not URLClick.objects.exists()

    def test_deleted_code_goes_to_default(self, client, short_url):
        short_url.url.delete()

        assert client.get('/abc123')['Location'] == DEFAULT_REDIRECT_URL

    def test_head_redirects_without_recording(self, client, short_url):
        assert client.head('/abc123').status_code == 302
        assert not URLClick.objects.exists()

    def test_post_is_not_allowed(self, client, short_url):
        assert client.post('/abc123').status_code == 405

    def test_reserved_path_without_slash_gets_slash_appended(self, client, db):
        response = client.get('/admin')

        assert response.status_code == 301
        assert response['Location'] == '/admin/'
