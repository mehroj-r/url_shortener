import pytest

INDEX = b'<!doctype html><title>Spur</title><div id="root"></div>'


@pytest.fixture
def frontend(tmp_path, settings):
    """A built web app, as the production image has it."""
    (tmp_path / 'assets').mkdir()
    (tmp_path / 'index.html').write_bytes(INDEX)
    (tmp_path / 'assets' / 'index-BnvZOjV8.js').write_text('console.log(1)')
    (tmp_path / 'theme.js').write_text('void 0')
    settings.FRONTEND_DIR = tmp_path
    return tmp_path


@pytest.mark.django_db
class TestWebApp:

    @pytest.mark.parametrize('path', ['/app/', '/app/links/42', '/app/join/abc'])
    def test_every_route_gets_the_page(self, client, frontend, path):
        response = client.get(path)

        assert response.status_code == 200
        assert response.content == INDEX
        assert response['Content-Type'] == 'text/html; charset=utf-8'
        assert response['Cache-Control'] == 'no-cache'

    def test_page_has_a_content_security_policy(self, client, frontend):
        policy = client.get('/app/')['Content-Security-Policy']

        assert "default-src 'self'" in policy
        assert "script-src 'self'" in policy
        assert "frame-ancestors 'none'" in policy

    def test_hashed_assets_are_cached_for_good(self, client, frontend):
        response = client.get('/app/assets/index-BnvZOjV8.js')

        assert response.status_code == 200
        assert 'javascript' in response['Content-Type']
        assert 'immutable' in response['Cache-Control']

    def test_other_files_are_cached_briefly(self, client, frontend):
        response = client.get('/app/theme.js')

        assert response.status_code == 200
        assert response['Cache-Control'] == 'max-age=60, public'

    def test_a_missing_asset_is_not_the_page(self, client, frontend):
        assert client.get('/app/assets/index-old.js').status_code == 404

    def test_only_reads(self, client, frontend):
        assert client.post('/app/').status_code == 405

    def test_missing_build(self, client, settings, tmp_path):
        settings.FRONTEND_DIR = tmp_path / 'missing'

        assert client.get('/app/').status_code == 404

    def test_root_and_bare_app_lead_to_the_app(self, client, frontend):
        assert client.get('/')['Location'] == '/app/'
        response = client.get('/app')
        assert (response.status_code, response['Location']) == (301, '/app/')

    def test_api_responses_carry_no_page_policy(self, client, frontend):
        assert 'Content-Security-Policy' not in client.get('/api/v1/shortener/urls/')
