import pytest

from apps.analytics.models import URLClick

CLICKS = '/api/v1/analytics/url-clicks/'


@pytest.mark.django_db
class TestClickAPI:

    def test_users_only_see_clicks_on_their_own_links(self, client, client_for, alice, bob, make_short_url):
        make_short_url(alice, code='alice1')
        make_short_url(bob, code='bob1')
        client.get('/alice1', HTTP_X_REAL_IP='203.0.113.1')
        client.get('/bob1', HTTP_X_REAL_IP='203.0.113.2')

        results = client_for(bob).get(CLICKS).json()['data']['results']

        assert [click['ipv4_address'] for click in results] == ['203.0.113.2']

    def test_click_includes_referer_and_time(self, client, client_for, alice, make_short_url):
        make_short_url(alice, code='alice1')
        client.get('/alice1', HTTP_REFERER='https://t.me/channel')

        click = client_for(alice).get(CLICKS).json()['data']['results'][0]

        assert click['referer'] == 'https://t.me/channel'
        assert click['created_at']

    def test_filter_by_short_url(self, client, client_for, alice, make_short_url):
        first = make_short_url(alice, code='first')
        make_short_url(alice, code='second')
        client.get('/first')
        client.get('/second')

        results = client_for(alice).get(CLICKS, {'short_url_id': first.pk}).json()['data']['results']

        assert [click['short_url'] for click in results] == [first.pk]

    def test_clicks_of_deleted_links_are_hidden(self, client, client_for, alice, make_short_url):
        short_url = make_short_url(alice, code='alice1')
        client.get('/alice1')

        short_url.delete()

        assert client_for(alice).get(CLICKS).json()['data']['count'] == 0
        assert URLClick.all_objects.count() == 1
