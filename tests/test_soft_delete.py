import pytest

from apps.account.models import User
from apps.analytics.models import URLClick
from apps.shortener.models import URL, ShortURL, URLCollection


@pytest.fixture
def tree(alice, make_collection, make_short_url):
    """alice -> collection -> url -> 2 short urls -> 50 clicks each."""
    collection = make_collection(alice)
    first = make_short_url(alice, code='first', collection=collection)
    second = ShortURL.objects.create(url=first.url, short_url='second')
    URLClick.objects.bulk_create(
        [URLClick(short_url=short_url) for short_url in (first, second) for _ in range(50)]
    )
    return collection, first.url


@pytest.mark.django_db
class TestSoftDelete:

    def test_cascades_in_a_constant_number_of_queries(self, tree, django_assert_max_num_queries):
        _, url = tree

        with django_assert_max_num_queries(6):
            url.delete()

        assert url.is_deleted
        assert not ShortURL.objects.exists()
        assert not URLClick.objects.exists()
        assert ShortURL.all_objects.count() == 2
        assert URLClick.all_objects.count() == 100

    def test_deleting_a_user_cascades_to_everything_they_own(self, tree, alice):
        alice.delete()

        assert not User.objects.filter(pk=alice.pk).exists()
        assert not URLCollection.objects.exists()
        assert not URL.objects.exists()
        assert not URLClick.objects.exists()

    def test_restore_brings_back_only_what_was_deleted_together(self, tree):
        _, url = tree
        earlier = ShortURL.objects.get(short_url='second')
        earlier.delete()

        url.delete()
        url.restore()

        assert URL.objects.filter(pk=url.pk).exists()
        assert list(ShortURL.objects.values_list('short_url', flat=True)) == ['first']
        assert URLClick.objects.count() == 50

    def test_queryset_delete_is_soft(self, tree):
        count, _ = URL.objects.all().delete()

        assert count == 1
        assert URL.all_objects.count() == 1
        assert not ShortURL.objects.exists()

    def test_hard_delete_removes_rows(self, tree):
        _, url = tree

        url.hard_delete()

        assert not URL.all_objects.exists()
        assert not URLClick.all_objects.exists()

    def test_destroy_endpoint_soft_deletes(self, tree, alice, client_for):
        collection, _ = tree

        response = client_for(alice).delete(f'/api/v1/shortener/url-collections/{collection.pk}/')

        assert response.status_code == 204
        assert URLCollection.all_objects.get(pk=collection.pk).is_deleted
        assert not URL.objects.exists()
