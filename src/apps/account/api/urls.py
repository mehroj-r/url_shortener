from django.urls import path

from apps.account.api.views import UserRegisterationView, LoginView, CustomTokenRefreshView, CustomTokenVerifyView

app_name = 'account'

urlpatterns = [
    path('register/', UserRegisterationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token-refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token-verify/', CustomTokenVerifyView.as_view(), name='token_verify'),
]