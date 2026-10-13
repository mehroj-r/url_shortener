from datetime import timedelta

import pytest
from django.utils import timezone

from apps.analytics.models import URLClick
from apps.analytics.user_agents import parse_user_agent, referer_domain

SUMMARY = '/api/v1/analytics/summary/'
IPHONE = ('Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) '
          'Version/18.1 Mobile/15E148 Safari/604.1')
WINDOWS_EDGE = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/130.0 Safari/537.36 Edg/130.0')
TELEGRAM_ANDROID = ('Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/129.0 Mobile Safari/537.36 Telegram-Android/11.2.3')


@pytest.mark.parametrize('ua, expected', [
    (IPHONE, ('Safari', 'iOS', 'mobile', False)),
    (WINDOWS_EDGE, ('Edge', 'Windows', 'desktop', False)),
    (TELEGRAM_ANDROID, ('Telegram', 'Android', 'mobile', False)),
    ('TelegramBot (like TwitterBot)', ('TelegramBot', '', 'bot', True)),
    ('WhatsApp/2.23.20.0 A', ('WhatsApp', '', 'bot', True)),
    ('curl/8.9.1', ('curl', '', 'bot', True)),
    ('', ('', '', 'other', False)),
])
def test_user_agent_classification(ua, expected):
    info = parse_user_agent(ua)

    assert (info.browser, info.os, info.device, info.is_bot) == expected


@pytest.mark.parametrize('referer, expected', [
    ('https://www.google.com/search?q=x', 'google.com'),
    ('https://t.me/channel/12', 't.me'),
    ('', None),
    (None, None),
])
def test_referer_domain(referer, expected):
    assert referer_domain(referer) == expected


@pytest.mark.django_db
class TestRecording:

    def test_redirect_stores_client_details(self, client, alice, make_short_url):
        make_short_url(alice, code='abc123')

        client.get('/abc123', HTTP_USER_AGENT=IPHONE, HTTP_REFERER='https://www.google.com/search')

        click = URLClick.objects.get()
        assert (click.browser, click.os, click.device, click.is_bot, click.referer_domain) == (
            'Safari', 'iOS', 'mobile', False, 'google.com')

    def test_expired_code_goes_to_default(self, client, settings, alice, make_short_url):
        settings.DEFAULT_REDIRECT_URL = 'https://default.example/'
        make_short_url(alice, code='gone', expires_at=timezone.now() - timedelta(seconds=1))

        assert client.get('/gone')['Location'] == 'https://default.example/'
        assert not URLClick.objects.exists()

    def test_app_is_reserved(self, client_for, alice, make_short_url):
        url = make_short_url(alice).url

        response = client_for(alice).post('/api/v1/shortener/short-urls/', {'url': url.pk, 'short_url': 'App'})

        assert response.status_code == 400


@pytest.mark.django_db
class TestSummary:

    @pytest.fixture
    def clicks(self, alice, bob, make_short_url, make_collection):
        collection = make_collection(alice)
        docs = make_short_url(alice, code='docs', collection=collection)
        blog = make_short_url(alice, code='blog')
        bobs = make_short_url(bob, code='bobs')
        now = timezone.now()

        def click(short_url, days_ago=0, **fields):
            created = URLClick.objects.create(short_url=short_url, **fields)
            URLClick.objects.filter(pk=created.pk).update(created_at=now - timedelta(days=days_ago))

        click(docs, referer_domain='t.me', browser='Telegram', os='Android', device='mobile', ipv4_address='1.1.1.1')
        click(docs, referer_domain='t.me', browser='Chrome', os='Windows', device='desktop', ipv4_address='1.1.1.1')
        click(blog, days_ago=2, browser='Safari', os='iOS', device='mobile', ipv4_address='2.2.2.2')
        click(blog, days_ago=40)
        click(docs, is_bot=True, device='bot')
        click(bobs)
        return {'docs': docs, 'blog': blog, 'collection': collection}

    def test_dashboard_summary(self, client_for, alice, clicks):
        data = client_for(alice).get(SUMMARY, {'days': 30}).json()['data']

        assert data['totals'] == {'clicks': 3, 'previous_clicks': 1, 'visitors': 2, 'bots': 1, 'links': 2}
        assert len(data['series']) == 30 and sum(day['clicks'] for day in data['series']) == 3
        assert data['series'][-1] == {'date': data['range']['end'], 'clicks': 2}
        assert sum(data['hours']) == 3
        assert [(row['code'], row['clicks']) for row in data['top_links']] == [('docs', 2), ('blog', 1)]
        assert data['link_clicks'] == [
            {'id': clicks['docs'].url_id, 'clicks': 2}, {'id': clicks['blog'].url_id, 'clicks': 1},
        ]
        assert data['referrers'] == [{'name': 't.me', 'clicks': 2}, {'name': None, 'clicks': 1}]
        assert {row['name']: row['clicks'] for row in data['devices']} == {'mobile': 2, 'desktop': 1}

    @pytest.mark.parametrize('scope, expected', [('url', 2), ('collection', 2)])
    def test_scoped_summary(self, client_for, alice, clicks, scope, expected):
        scope_id = clicks['docs'].url_id if scope == 'url' else clicks['collection'].pk

        data = client_for(alice).get(SUMMARY, {scope: scope_id}).json()['data']

        assert data['totals']['clicks'] == expected

    def test_other_users_links_are_out_of_scope(self, client_for, bob, clicks):
        data = client_for(bob).get(SUMMARY, {'url': clicks['docs'].url_id}).json()['data']

        assert data['totals']['clicks'] == 0

    @pytest.mark.parametrize('params', [{'days': 0}, {'days': 400}, {'tz': 'Mars/Olympus'}])
    def test_rejects_bad_parameters(self, client_for, alice, params):
        assert client_for(alice).get(SUMMARY, params).status_code == 400

    def test_click_list_carries_details(self, client_for, alice, clicks):
        rows = client_for(alice).get('/api/v1/analytics/url-clicks/', {'is_bot': 'false'}).json()['data']['results']

        assert len(rows) == 4
        assert {'code', 'link', 'link_name', 'browser', 'os', 'device', 'referer_domain'} <= set(rows[0])
