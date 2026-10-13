from itertools import count

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.account.models import User
from apps.shortener.models import URL, ShortURL, URLCollection

PASSWORD = 'correct-horse-battery-staple'


@pytest.fixture(autouse=True)
def _reset_throttling():
    cache.clear()


@pytest.fixture
def make_user(db):
    numbers = count(1)

    def make_user(**kwargs):
        n = next(numbers)
        kwargs.setdefault('email', f'user{n}@example.com')
        kwargs.setdefault('first_name', 'Test')
        kwargs.setdefault('last_name', f'User{n}')
        return User.objects.create_user(password=kwargs.pop('password', PASSWORD), **kwargs)

    return make_user


@pytest.fixture
def alice(make_user):
    return make_user(email='Alice@example.com', username='Alice', phone='+998901234567')


@pytest.fixture
def bob(make_user):
    return make_user(email='bob@example.com', username='bob')


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def client_for():
    def client_for(user):
        client = APIClient()
        client.force_authenticate(user)
        return client

    return client_for


@pytest.fixture
def make_short_url():
    def make_short_url(user, code='abc123', target='https://example.com/page', collection=None, **kwargs):
        url = URL.objects.create(name='Example', url=target, user=user, collection=collection)
        return ShortURL.objects.create(url=url, short_url=code, **kwargs)

    return make_short_url


@pytest.fixture
def make_collection():
    def make_collection(user, name='Work'):
        return URLCollection.objects.create(user=user, name=name)

    return make_collection
