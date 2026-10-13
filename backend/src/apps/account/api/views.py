from django.contrib.auth.models import update_last_login
from rest_framework import generics, mixins, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView, TokenVerifyView

from apps.account.api.serializers import (
    ChangePasswordSerializer,
    InviteSerializer,
    LoginSerializer,
    ProfileSerializer,
    UserRegistrationSerializer,
    usable_invites,
)
from apps.account.models import Invite
from core.api.throttles import ClientIPScopedRateThrottle
from core.api.views import BaseAPIView, BaseAPIViewSet


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


class InviteCheckView(CredentialsAPIView):
    """Tells the sign-up page whether an invite token can still be used, and who sent it."""

    def get(self, request, token):
        invite = usable_invites().select_related('created_by').filter(token=token).first()
        if invite is None:
            return Response({'valid': False, 'invited_by': None})
        return Response({'valid': True, 'invited_by': invite.created_by.first_name})


class ProfileView(BaseAPIView, generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    user_field = None

    def get_object(self):
        return self.request.user


class ChangePasswordView(BaseAPIView):
    serializer_class = ChangePasswordSerializer
    user_field = None

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password changed.'})


class InviteViewSet(BaseAPIViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = Invite.objects.select_related('used_by').order_by('-created_at')
    serializer_class = InviteSerializer
    user_field = 'created_by'

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        if instance.used_at is not None:
            raise ValidationError({'detail': 'This invite has already been used.'})
        instance.delete()
