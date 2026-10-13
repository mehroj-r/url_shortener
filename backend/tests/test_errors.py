import pytest
from django.db import IntegrityError

from apps.shortener.api.views import URLViewSet


@pytest.mark.django_db
class TestErrorResponses:

    def test_unhandled_error_is_generic_and_logged(self, client_for, alice, monkeypatch, caplog):
        def boom(self, request, *args, **kwargs):
            raise RuntimeError('secret internal detail')

        monkeypatch.setattr(URLViewSet, 'list', boom)

        response = client_for(alice).get('/api/v1/shortener/urls/')

        assert response.status_code == 500
        assert response.json() == {
            'success': False,
            'message': 'NOT OK',
            'error': {'detail': 'Internal server error.'},
        }
        assert 'secret internal detail' in caplog.text

    def test_integrity_error_is_generic(self, client_for, alice, monkeypatch):
        def conflict(self, request, *args, **kwargs):
            raise IntegrityError('duplicate key value violates unique constraint "secret_name"')

        monkeypatch.setattr(URLViewSet, 'list', conflict)

        response = client_for(alice).get('/api/v1/shortener/urls/')

        assert response.status_code == 400
        assert 'secret_name' not in response.content.decode()
        assert response.json()['error'] == {'detail': 'The request conflicts with existing data.'}
