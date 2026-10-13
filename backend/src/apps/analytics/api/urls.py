from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.analytics.api.views import AnalyticsSummaryView, URLClickViewSet

app_name = 'analytics'

router = DefaultRouter()
router.register(r'url-clicks', URLClickViewSet, basename='url-clicks')

urlpatterns = [
    path('summary/', AnalyticsSummaryView.as_view(), name='summary'),
    *router.urls
]
