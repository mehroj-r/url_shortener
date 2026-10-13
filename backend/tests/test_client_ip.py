import pytest
from django.test import RequestFactory

from core.utils.request import get_client_ip


def ip_for(remote_addr='172.18.0.1', forwarded=None):
    headers = {'REMOTE_ADDR': remote_addr}
    if forwarded is not None:
        headers['HTTP_X_FORWARDED_FOR'] = forwarded
    return get_client_ip(RequestFactory().get('/', **headers))


@pytest.mark.parametrize(
    ('remote_addr', 'forwarded', 'expected'),
    [
        # The host's proxy appends the visitor's address
        ('172.18.0.1', '203.0.113.7', '203.0.113.7'),
        # Whatever the client sent sits to the left of it and is ignored
        ('172.18.0.1', '198.51.100.1, 203.0.113.7', '203.0.113.7'),
        # Trusted hops on the right are skipped
        ('172.18.0.1', '203.0.113.7, 10.0.0.5, 127.0.0.1', '203.0.113.7'),
        ('172.18.0.1', '2001:db8::1', '2001:db8::1'),
        # A request from outside the trusted networks is taken at face value
        ('203.0.113.9', '198.51.100.1', '203.0.113.9'),
        # No header: the connecting address
        ('172.18.0.1', None, '172.18.0.1'),
        # Every hop private: the left-most one
        ('172.18.0.1', '192.168.1.20, 10.0.0.5', '192.168.1.20'),
        # Garbage where an address should be
        ('172.18.0.1', 'not-an-ip', None),
        ('', None, None),
    ],
)
def test_client_ip(remote_addr, forwarded, expected):
    assert ip_for(remote_addr, forwarded) == expected
