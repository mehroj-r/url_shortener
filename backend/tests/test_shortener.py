import pytest

from apps.shortener.models import URL, ShortURL, URLCollection

API = '/api/v1/shortener'


@pytest.mark.django_db
class TestOwnership:

    def test_lists_only_own_objects(self, client_for, alice, bob, make_short_url, make_collection):
        make_short_url(alice, code='alice1')
        make_collection(alice)

        bob_client = client_for(bob)
        for path in ['urls', 'short-urls', 'url-collections']:
            assert bob_client.get(f'{API}/{path}/').json()['data']['count'] == 0, path

    def test_short_url_cannot_point_at_another_users_url(self, client_for, alice, bob, make_short_url):
        alice_url = make_short_url(alice, code='alice1').url

        response = client_for(bob).post(f'{API}/short-urls/', {'url': alice_url.pk, 'short_url': 'peek'})

        assert response.status_code == 400
        assert 'url' in response.json()['error']
        assert not ShortURL.objects.filter(short_url='peek').exists()

    def test_short_url_cannot_be_repointed_at_another_users_url(self, client_for, alice, bob, make_short_url):
        alice_url = make_short_url(alice, code='alice1').url
        bob_short_url = make_short_url(bob, code='bob1')

        response = client_for(bob).patch(f'{API}/short-urls/{bob_short_url.pk}/', {'url': alice_url.pk})

        assert response.status_code == 400
        bob_short_url.refresh_from_db()
        assert bob_short_url.url.user == bob

    def test_url_cannot_join_another_users_collection(self, client_for, alice, bob, make_collection):
        collection = make_collection(alice)

        response = client_for(bob).post(
            f'{API}/urls/', {'name': 'x', 'url': 'https://bob.example', 'collection': collection.pk},
        )

        assert response.status_code == 400
        assert 'collection' in response.json()['error']

    def test_nested_create_uses_the_collection_from_the_path(self, client_for, alice, make_collection):
        work, home = make_collection(alice, 'Work'), make_collection(alice, 'Home')

        response = client_for(alice).post(
            f'{API}/url-collections/{work.pk}/urls/',
            {'name': 'Docs', 'url': 'https://docs.example', 'collection': home.pk},
        )

        assert response.status_code == 201
        assert response.json()['data']['collection'] == work.pk
        assert URL.objects.get(name='Docs').collection == work

    def test_nested_create_in_another_users_collection_is_404(self, client_for, alice, bob, make_collection):
        collection = make_collection(alice)

        response = client_for(bob).post(
            f'{API}/url-collections/{collection.pk}/urls/', {'name': 'x', 'url': 'https://bob.example'},
        )

        assert response.status_code == 404
        assert not URL.objects.filter(collection=collection).exists()

    def test_nested_short_url_create_under_another_users_url_is_404(self, client_for, alice, bob, make_short_url):
        alice_url = make_short_url(alice, code='alice1').url

        response = client_for(bob).post(f'{API}/urls/{alice_url.pk}/short-urls/', {'short_url': 'peek'})

        assert response.status_code == 404
        assert not ShortURL.objects.filter(short_url='peek').exists()

    def test_nested_lists_only_children_of_the_parent(self, client_for, alice, make_collection):
        work, home = make_collection(alice, 'Work'), make_collection(alice, 'Home')
        URL.objects.create(name='a', url='https://a.example', user=alice, collection=work)
        URL.objects.create(name='b', url='https://b.example', user=alice, collection=home)

        response = client_for(alice).get(f'{API}/url-collections/{work.pk}/urls/')

        assert [item['name'] for item in response.json()['data']['results']] == ['a']

    def test_non_numeric_ids_are_404(self, client_for, alice):
        assert client_for(alice).get(f'{API}/url-collections/abc/urls/').status_code == 404
        assert client_for(alice).get(f'{API}/urls/abc/').status_code == 404


@pytest.mark.django_db
class TestCollections:

    def test_names_are_unique_per_user(self, client_for, alice, bob, make_collection):
        make_collection(alice, 'Work')

        assert client_for(bob).post(f'{API}/url-collections/', {'name': 'Work'}).status_code == 201
        response = client_for(alice).post(f'{API}/url-collections/', {'name': 'Work'})
        assert response.status_code == 400
        assert 'name' in response.json()['error']

    def test_rename_to_an_existing_name_is_rejected(self, client_for, alice, make_collection):
        make_collection(alice, 'Work')
        home = make_collection(alice, 'Home')
        alice_client = client_for(alice)

        response = alice_client.patch(f'{API}/url-collections/{home.pk}/', {'name': 'Work'})
        assert response.status_code == 400
        assert 'name' in response.json()['error']

        assert alice_client.patch(f'{API}/url-collections/{home.pk}/', {'name': 'Home'}).status_code == 200

    def test_name_is_free_again_after_delete(self, client_for, alice, make_collection):
        make_collection(alice, 'Work').delete()

        assert client_for(alice).post(f'{API}/url-collections/', {'name': 'Work'}).status_code == 201
        assert URLCollection.all_objects.filter(user=alice, name='Work').count() == 2


@pytest.mark.django_db
class TestShortCodes:

    @pytest.fixture
    def url(self, alice):
        return URL.objects.create(name='Example', url='https://example.com', user=alice)

    def test_generated_when_omitted(self, client_for, alice, url):
        response = client_for(alice).post(f'{API}/short-urls/', {'url': url.pk})

        assert response.status_code == 201
        code = response.json()['data']['short_url']
        assert len(code) == ShortURL.CODE_LENGTH and code.isalnum()

    def test_generated_in_nested_create(self, client_for, alice, url):
        response = client_for(alice).post(f'{API}/urls/{url.pk}/short-urls/', {})

        assert response.status_code == 201
        assert response.json()['data']['url'] == url.pk

    @pytest.mark.parametrize('code', ['admin', 'API', 'static', '__debug__', 'my link', 'a/b', 'é', 'x' * 65])
    def test_rejects_invalid_or_reserved_codes(self, client_for, alice, url, code):
        response = client_for(alice).post(f'{API}/short-urls/', {'url': url.pk, 'short_url': code})

        assert response.status_code == 400
        assert 'short_url' in response.json()['error']

    @pytest.mark.parametrize('code', ['my-link', 'my_link', 'Promo2026'])
    def test_accepted_codes_resolve(self, client, client_for, alice, url, code):
        assert client_for(alice).post(f'{API}/short-urls/', {'url': url.pk, 'short_url': code}).status_code == 201

        response = client.get(f'/{code}')

        assert response.status_code == 302
        assert response['Location'] == 'https://example.com'

    def test_deleted_code_is_never_reused(self, client_for, alice, bob, make_short_url):
        make_short_url(alice, code='promo').delete()
        bob_url = URL.objects.create(name='Bob', url='https://bob.example', user=bob)

        response = client_for(bob).post(f'{API}/short-urls/', {'url': bob_url.pk, 'short_url': 'promo'})

        assert response.status_code == 400
        assert 'short_url' in response.json()['error']
