from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from apps.account.api.serializers import UserRegistrationSerializer, LoginSerializer
from core.api.views import BaseAPIView


class UserRegisterationView(BaseAPIView, generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = []
    authentication_classes = []


class LoginView(BaseAPIView):
    serializer_class = LoginSerializer
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data, status=200)


class CustomTokenRefreshView(BaseAPIView, TokenRefreshView):
    permission_classes = []
    authentication_classes = []


class CustomTokenVerifyView(BaseAPIView, TokenVerifyView):
    permission_classes = []
    authentication_classes = []