import pytest
from django.urls import reverse

from apps.account.models import User
from conftest import PASSWORD

REGISTER = '/api/v1/auth/register/'
LOGIN = '/api/v1/auth/login/'
LOGOUT = '/api/v1/auth/logout/'
REFRESH = '/api/v1/auth/token-refresh/'
VERIFY = '/api/v1/auth/token-verify/'


def registration(invite, **overrides):
    data = {
        'first_name': 'Carol',
        'last_name': 'Smith',
        'email': 'carol@example.com',
        'password': PASSWORD,
        'password_repeat': PASSWORD,
        'invite': invite,
    }
    return {**data, **overrides}


@pytest.mark.django_db
class TestRegistration:

    def test_creates_user_with_hashed_password(self, api_client, invite_token):
        response = api_client.post(REGISTER, registration(invite_token), format='json')

        assert response.status_code == 201
        assert 'password' not in response.json()['data']
        user = User.objects.get(email='carol@example.com')
        assert user.check_password(PASSWORD)
        assert user.password != PASSWORD

    def test_rejects_weak_password(self, api_client, invite_token):
        data = registration(invite_token, password='1', password_repeat='1')
        response = api_client.post(REGISTER, data, format='json')

        assert response.status_code == 400
        assert 'password' in response.json()['error']
        assert not User.objects.filter(email='carol@example.com').exists()

    def test_rejects_password_similar_to_email(self, api_client, invite_token):
        data = registration(invite_token, email='carolsmith@example.com', password='carolsmith',
                            password_repeat='carolsmith')
        response = api_client.post(REGISTER, data, format='json')

        assert response.status_code == 400

    def test_rejects_mismatched_passwords(self, api_client, invite_token):
        data = registration(invite_token, password_repeat='something-else-entirely')
        response = api_client.post(REGISTER, data, format='json')

        assert response.status_code == 400
        assert set(response.json()['error']) == {'password', 'password_repeat'}

    @pytest.mark.parametrize('field, value', [
        ('email', 'ALICE@example.com'),
        ('username', 'alice'),
        ('phone', '+998901234567'),
    ])
    def test_rejects_identifiers_already_taken(self, api_client, alice, field, value, invite_token):
        response = api_client.post(REGISTER, registration(invite_token, **{field: value}), format='json')

        assert response.status_code == 400
        assert field in response.json()['error']

    def test_email_of_deleted_user_stays_taken(self, api_client, alice, invite_token):
        alice.delete()

        response = api_client.post(REGISTER, registration(invite_token, email='alice@example.com'), format='json')

        assert response.status_code == 400
        assert 'email' in response.json()['error']


@pytest.mark.django_db
class TestLogin:

    @pytest.mark.parametrize('credentials', [
        {'email': 'alice@EXAMPLE.com'},
        {'username': 'ALICE'},
        {'phone': '+998901234567'},
    ])
    def test_logs_in_with_any_identifier_case_insensitively(self, api_client, alice, credentials):
        response = api_client.post(LOGIN, {**credentials, 'password': PASSWORD}, format='json')

        assert response.status_code == 200
        data = response.json()['data']
        assert data['user']['email'] == 'Alice@example.com'
        assert {'access', 'refresh'} <= set(data['token'])

    @pytest.mark.parametrize('credentials', [{'phone': 'not-a-phone'}, {'username': 'ghost'}])
    def test_unknown_or_malformed_identifier_is_a_normal_login_error(self, api_client, alice, credentials):
        response = api_client.post(LOGIN, {**credentials, 'password': PASSWORD}, format='json')

        assert response.status_code == 400
        assert 'credentials' in response.json()['error']

    def test_updates_last_login(self, api_client, alice):
        api_client.post(LOGIN, {'email': alice.email, 'password': PASSWORD}, format='json')

        alice.refresh_from_db()
        assert alice.last_login is not None

    def test_same_error_for_unknown_user_and_wrong_password(self, api_client, alice):
        unknown = api_client.post(LOGIN, {'email': 'nobody@example.com', 'password': PASSWORD}, format='json')
        wrong = api_client.post(LOGIN, {'email': alice.email, 'password': 'wrong-password'}, format='json')

        assert unknown.status_code == wrong.status_code == 400
        assert unknown.json() == wrong.json()

    def test_inactive_user_cannot_log_in(self, api_client, alice):
        alice.is_active = False
        alice.save()

        response = api_client.post(LOGIN, {'email': alice.email, 'password': PASSWORD}, format='json')

        assert response.status_code == 400

    def test_deleted_user_cannot_log_in_or_use_existing_token(self, api_client, alice):
        login = api_client.post(LOGIN, {'email': alice.email, 'password': PASSWORD}, format='json')
        access = login.json()['data']['token']['access']

        alice.delete()

        response = api_client.post(LOGIN, {'email': alice.email, 'password': PASSWORD}, format='json')
        assert response.status_code == 400
        response = api_client.get('/api/v1/shortener/urls/', HTTP_AUTHORIZATION=f'Bearer {access}')
        assert response.status_code == 401

    def test_is_rate_limited_per_client_ip(self, api_client, alice):
        def attempt(ip):
            return api_client.post(
                LOGIN, {'email': alice.email, 'password': 'wrong'}, format='json', HTTP_X_FORWARDED_FOR=ip,
            )

        statuses = [attempt('203.0.113.1').status_code for _ in range(11)]

        assert statuses[:10] == [400] * 10
        assert statuses[10] == 429
        # A client-sent X-Forwarded-For doesn't help (the proxy appends the real address);
        # another client IP is unaffected
        assert api_client.post(
            LOGIN, {'email': alice.email, 'password': 'wrong'}, format='json',
            HTTP_X_FORWARDED_FOR='198.51.100.7, 203.0.113.1',
        ).status_code == 429
        assert attempt('203.0.113.2').status_code == 400


@pytest.mark.django_db
def test_token_endpoints_are_not_throttled(api_client, alice):
    login = api_client.post(LOGIN, {'email': alice.email, 'password': PASSWORD}, format='json')
    access = login.json()['data']['token']['access']

    statuses = {api_client.post(VERIFY, {'token': access}, format='json').status_code for _ in range(15)}

    assert statuses == {200}


@pytest.mark.django_db
def test_logout_blacklists_refresh_token(api_client, alice):
    login = api_client.post(LOGIN, {'email': alice.email, 'password': PASSWORD}, format='json')
    refresh = login.json()['data']['token']['refresh']

    assert api_client.post(LOGOUT, {'refresh': refresh}, format='json').status_code == 200
    assert api_client.post(REFRESH, {'refresh': refresh}, format='json').status_code == 401


@pytest.fixture
def superuser_client(client, make_user):
    admin = make_user(email='admin@example.com', is_staff=True, is_superuser=True)
    client.force_login(admin)
    return client


@pytest.mark.django_db
class TestUserAdmin:

    def test_pages_render(self, superuser_client, alice):
        for url in [
            reverse('admin:account_user_changelist'),
            reverse('admin:account_user_add'),
            reverse('admin:account_user_change', args=[alice.pk]),
            reverse('admin:auth_user_password_change', args=[alice.pk]),
        ]:
            assert superuser_client.get(url).status_code == 200, url

    def test_add_user_hashes_password(self, superuser_client):
        response = superuser_client.post(reverse('admin:account_user_add'), {
            'email': 'dave@example.com',
            'first_name': 'Dave',
            'last_name': 'Jones',
            'usable_password': 'true',
            'password1': PASSWORD,
            'password2': PASSWORD,
        })

        assert response.status_code == 302, response.content
        assert User.objects.get(email='dave@example.com').check_password(PASSWORD)

    def test_editing_user_keeps_password(self, superuser_client, alice):
        response = superuser_client.post(reverse('admin:account_user_change', args=[alice.pk]), {
            'email': alice.email,
            'first_name': 'Alicia',
            'last_name': alice.last_name,
            'username': alice.username,
            'phone': '+998901234567',
            'is_active': 'on',
        })

        assert response.status_code == 302, response.content
        alice.refresh_from_db()
        assert alice.first_name == 'Alicia'
        assert alice.check_password(PASSWORD)
