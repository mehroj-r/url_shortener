from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.account.api.views import (
    UserRegisterationView,
    LoginView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    LogoutView,
    InviteCheckView,
    InviteViewSet,
    ProfileView,
    ChangePasswordView,
)

app_name = 'account'

router = SimpleRouter()
router.register(r'invites', InviteViewSet, basename='invites')

urlpatterns = [
    path('register/', UserRegisterationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token-refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token-verify/', CustomTokenVerifyView.as_view(), name='token_verify'),
    path('me/', ProfileView.as_view(), name='me'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('invites/check/<str:token>/', InviteCheckView.as_view(), name='invite_check'),
    *router.urls,
]
