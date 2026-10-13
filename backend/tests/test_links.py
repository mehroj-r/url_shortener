from datetime import timedelta

import pytest
from django.utils import timezone

from apps.analytics.models import URLClick
from apps.shortener.models import URL, ShortURL, Tag

LINKS = '/api/v1/shortener/urls/'


@pytest.fixture
def tags(alice, bob):
    return {
        'work': Tag.objects.create(user=alice, name='Work', color='blue'),
        'bobs': Tag.objects.create(user=bob, name='Bobs'),
    }


@pytest.mark.django_db
class TestCreateLink:

    def test_one_call_creates_link_and_code(self, client_for, alice, tags, make_collection):
        collection = make_collection(alice)
        expires = (timezone.now() + timedelta(days=2)).isoformat()

        response = client_for(alice).post(LINKS, {
            'name': 'CV', 'url': 'https://cv.example', 'code': 'cv-2026', 'expires_at': expires,
            'collection': collection.pk, 'tags': [tags['work'].pk],
        })

        assert response.status_code == 201, response.json()
        data = response.json()['data']
        assert data['tags'] == [tags['work'].pk] and data['status'] == 'active' and data['clicks'] == 0
        assert [c['short_url'] for c in data['short_urls']] == ['cv-2026']
        assert ShortURL.objects.get(short_url='cv-2026').expires_at is not None

    def test_code_is_generated_when_omitted(self, client_for, alice):
        data = client_for(alice).post(LINKS, {'name': 'x', 'url': 'https://x.example'}).json()['data']

        assert len(data['short_urls'][0]['short_url']) == ShortURL.CODE_LENGTH

    @pytest.mark.parametrize('field, value', [
        ('code', 'app'), ('code', 'has space'), ('expires_at', '2001-01-01T00:00:00Z'),
    ])
    def test_rejects_bad_code_or_expiry(self, client_for, alice, field, value):
        response = client_for(alice).post(LINKS, {'name': 'x', 'url': 'https://x.example', field: value})

        assert response.status_code == 400
        assert field in response.json()['error']
        assert not URL.objects.exists()

    def test_cannot_use_another_users_tag(self, client_for, alice, tags):
        response = client_for(alice).post(LINKS, {'name': 'x', 'url': 'https://x.example', 'tags': [tags['bobs'].pk]})

        assert response.status_code == 400
        assert 'tags' in response.json()['error']


@pytest.mark.django_db
class TestListLinks:

    @pytest.fixture
    def links(self, alice, tags, make_collection, make_short_url):
        collection = make_collection(alice)
        docs = make_short_url(alice, code='docs', target='https://docs.example', collection=collection)
        blog = make_short_url(alice, code='blog', target='https://blog.example')
        old = make_short_url(alice, code='old', target='https://old.example',
                             expires_at=timezone.now() - timedelta(days=1))
        off = make_short_url(alice, code='off', target='https://off.example', is_active=False)
        docs.url.tags.add(tags['work'])
        URLClick.objects.bulk_create([URLClick(short_url=blog) for _ in range(3)] + [
            URLClick(short_url=docs), URLClick(short_url=docs, is_bot=True),
        ])
        return {'docs': docs.url, 'blog': blog.url, 'old': old.url, 'off': off.url, 'collection': collection}

    def names(self, client, **params):
        return [link['url'] for link in client.get(LINKS, params).json()['data']['results']]

    def test_counts_human_clicks_only(self, client_for, alice, links):
        rows = {link['url']: link for link in client_for(alice).get(LINKS).json()['data']['results']}

        assert rows['https://blog.example']['clicks'] == 3
        assert rows['https://docs.example']['clicks'] == 1
        assert rows['https://blog.example']['last_clicked_at']

    def test_status_reflects_codes(self, client_for, alice, links):
        rows = {link['url']: link['status'] for link in client_for(alice).get(LINKS).json()['data']['results']}

        assert rows == {'https://docs.example': 'active', 'https://blog.example': 'active',
                        'https://old.example': 'expired', 'https://off.example': 'inactive'}

    def test_filters_search_and_ordering(self, client_for, alice, tags, links):
        client = client_for(alice)

        assert self.names(client, collection=links['collection'].pk) == ['https://docs.example']
        assert set(self.names(client, collection='none')) == {
            'https://blog.example', 'https://old.example', 'https://off.example'}
        assert self.names(client, tag=tags['work'].pk) == ['https://docs.example']
        assert self.names(client, status='expired') == ['https://old.example']
        assert self.names(client, status='inactive') == ['https://off.example']
        assert self.names(client, search='blo') == ['https://blog.example']
        assert self.names(client, ordering='-clicks')[:2] == ['https://blog.example', 'https://docs.example']

    def test_page_size(self, client_for, alice, links):
        assert len(client_for(alice).get(LINKS, {'page_size': 2}).json()['data']['results']) == 2

    def test_bulk_actions(self, client_for, alice, tags, links, make_collection):
        client = client_for(alice)
        ids = [links['blog'].pk, links['old'].pk]
        target = make_collection(alice, 'Archive')

        def bulk(**body):
            return client.post(f'{LINKS}bulk/', {'ids': ids, **body}, format='json')

        assert bulk(action='move', collection=target.pk).json()['data'] == {'count': 2}
        assert set(URL.objects.filter(collection=target).values_list('pk', flat=True)) == set(ids)
        bulk(action='add_tag', tag=tags['work'].pk)
        assert tags['work'].urls.count() == 3
        bulk(action='deactivate')
        assert not ShortURL.objects.filter(url_id__in=ids, is_active=True).exists()
        bulk(action='delete')
        assert not URL.objects.filter(pk__in=ids).exists()
        assert URL.all_objects.filter(pk__in=ids).count() == 2

    def test_bulk_ignores_other_users_links(self, client_for, bob, links):
        response = client_for(bob).post(f'{LINKS}bulk/', {'ids': [links['blog'].pk], 'action': 'delete'},
                                        format='json')

        assert response.json()['data'] == {'count': 0}
        assert URL.objects.filter(pk=links['blog'].pk).exists()

    def test_bulk_validates_its_arguments(self, client_for, alice, links):
        response = client_for(alice).post(f'{LINKS}bulk/', {'ids': [links['blog'].pk], 'action': 'move'},
                                          format='json')

        assert response.status_code == 400


@pytest.mark.django_db
class TestTags:

    def test_crud_with_link_counts(self, client_for, alice, make_short_url):
        client = client_for(alice)
        tag = client.post('/api/v1/shortener/tags/', {'name': 'Promo', 'color': 'violet'}).json()['data']
        make_short_url(alice).url.tags.add(tag['id'])

        listed = client.get('/api/v1/shortener/tags/').json()['data']['results']

        assert listed == [{**tag, 'link_count': 1}]
        assert client.post('/api/v1/shortener/tags/', {'name': 'PROMO'}).status_code == 400
        assert client.post('/api/v1/shortener/tags/', {'name': 'x', 'color': 'neon'}).status_code == 400

    def test_tags_are_private(self, client_for, alice, bob):
        Tag.objects.create(user=alice, name='Secret')

        assert client_for(bob).get('/api/v1/shortener/tags/').json()['data']['count'] == 0
        assert client_for(bob).post('/api/v1/shortener/tags/', {'name': 'Secret'}).status_code == 201


@pytest.mark.django_db
def test_new_collections_take_the_next_line_colour(client_for, alice):
    client = client_for(alice)
    colours = [client.post('/api/v1/shortener/url-collections/', {'name': f'c{i}'}).json()['data']['color']
               for i in range(7)]
    chosen = client.post('/api/v1/shortener/url-collections/', {'name': 'mine', 'color': 'teal'}).json()['data']

    assert colours == ['red', 'blue', 'green', 'violet', 'amber', 'teal', 'red']
    assert chosen['color'] == 'teal'


@pytest.mark.django_db
def test_collections_report_link_and_click_counts(client_for, alice, make_collection, make_short_url):
    collection = make_collection(alice)
    short_url = make_short_url(alice, collection=collection)
    URLClick.objects.bulk_create([URLClick(short_url=short_url) for _ in range(4)])

    data = client_for(alice).get('/api/v1/shortener/url-collections/').json()['data']['results'][0]

    assert (data['link_count'], data['clicks']) == (1, 4)
