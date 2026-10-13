from .base import *

SECRET_KEY = 'test-only-secret-key-not-used-anywhere-else-0123456789'

# Fast hashing keeps the auth tests quick.
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# Independent of any local .env
DEBUG = False
REST_FRAMEWORK['EXCEPTION_HANDLER'] = 'core.api.exceptions.custom_exception_handler'
REST_FRAMEWORK['TEST_REQUEST_DEFAULT_FORMAT'] = 'json'
