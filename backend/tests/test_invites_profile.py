from datetime import timedelta

import pytest
from django.utils import timezone

from apps.account.models import Invite, User
from conftest import PASSWORD

INVITES = '/api/v1/auth/invites/'


def signup(api_client, token, email='newbie@example.com'):
    return api_client.post('/api/v1/auth/register/', {
        'first_name': 'New', 'last_name': 'Person', 'email': email,
        'password': PASSWORD, 'password_repeat': PASSWORD, 'invite': token,
    }, format='json')


@pytest.mark.django_db
class TestInvites:

    def test_create_list_and_use_an_invite(self, api_client, client_for, alice):
        alice_client = client_for(alice)
        invite = alice_client.post(INVITES, {'note': 'For Aziz', 'expires_in_days': 3}).json()['data']
        assert invite['status'] == 'pending' and invite['token']

        check = api_client.get(f"{INVITES}check/{invite['token']}/").json()['data']
        assert check == {'valid': True, 'invited_by': alice.first_name}

        assert signup(api_client, invite['token']).status_code == 201

        listed = alice_client.get(INVITES).json()['data']['results'][0]
        assert listed['status'] == 'used' and listed['used_by_name'] == 'New Person'

    def test_invite_is_single_use(self, api_client, alice):
        token = Invite.objects.create(created_by=alice).token
        assert signup(api_client, token).status_code == 201

        response = signup(api_client, token, email='second@example.com')

        assert response.status_code == 400
        assert 'invite' in response.json()['error']
        assert not User.objects.filter(email='second@example.com').exists()

    @pytest.mark.parametrize('token', ['made-up-token', None])
    def test_signup_needs_a_valid_invite(self, api_client, alice, token):
        response = signup(api_client, token or Invite.objects.create(
            created_by=alice, expires_at=timezone.now() - timedelta(minutes=1)).token)

        assert response.status_code == 400
        assert 'invite' in response.json()['error']

    def test_check_reports_invalid_tokens(self, api_client, db):
        assert api_client.get(f'{INVITES}check/nope/').json()['data'] == {'valid': False, 'invited_by': None}

    def test_users_only_see_and_revoke_their_own(self, client_for, alice, bob):
        invite = Invite.objects.create(created_by=alice)

        assert client_for(bob).get(INVITES).json()['data']['count'] == 0
        assert client_for(bob).delete(f'{INVITES}{invite.pk}/').status_code == 404
        assert client_for(alice).delete(f'{INVITES}{invite.pk}/').status_code == 204

    def test_used_invites_cannot_be_revoked(self, api_client, client_for, alice):
        invite = Invite.objects.create(created_by=alice)
        signup(api_client, invite.token)

        assert client_for(alice).delete(f'{INVITES}{invite.pk}/').status_code == 400


@pytest.mark.django_db
class TestProfile:

    def test_read_and_update_profile(self, client_for, alice):
        client = client_for(alice)
        assert client.get('/api/v1/auth/me/').json()['data']['email'] == 'Alice@example.com'

        response = client.patch('/api/v1/auth/me/', {'first_name': 'Alicia', 'email': 'evil@example.com'})

        assert response.status_code == 200
        alice.refresh_from_db()
        assert alice.first_name == 'Alicia' and alice.email == 'Alice@example.com'

    def test_username_must_stay_unique(self, client_for, alice, bob):
        response = client_for(bob).patch('/api/v1/auth/me/', {'username': 'ALICE'})

        assert response.status_code == 400
        assert 'username' in response.json()['error']

    def test_change_password(self, client_for, alice):
        client = client_for(alice)
        wrong = client.post('/api/v1/auth/change-password/', {'current_password': 'nope', 'new_password': 'x'})
        assert set(wrong.json()['error']) == {'current_password', 'new_password'}

        response = client.post('/api/v1/auth/change-password/',
                               {'current_password': PASSWORD, 'new_password': 'another-long-passphrase'})

        assert response.status_code == 200
        alice.refresh_from_db()
        assert alice.check_password('another-long-passphrase')
