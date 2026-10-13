from django.contrib.auth.models import update_last_login
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView, TokenVerifyView

from apps.account.api.serializers import UserRegistrationSerializer, LoginSerializer
from core.api.throttles import ClientIPScopedRateThrottle
from core.api.views import BaseAPIView


class AuthAPIView(BaseAPIView):
    """Public auth endpoint."""
    permission_classes = []
    authentication_classes = []


class CredentialsAPIView(AuthAPIView):
    """Takes a password, so it is rate limited per client IP against guessing."""
    throttle_classes = [ClientIPScopedRateThrottle]
    throttle_scope = 'auth'


class UserRegisterationView(CredentialsAPIView, generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer


class LoginView(CredentialsAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update_last_login(None, serializer.validated_data['user'])
        return Response(data=serializer.data, status=200)


class CustomTokenRefreshView(AuthAPIView, TokenRefreshView):
    ...


class CustomTokenVerifyView(AuthAPIView, TokenVerifyView):
    ...


class LogoutView(AuthAPIView, TokenBlacklistView):
    """Blacklists the given refresh token."""
    ...
