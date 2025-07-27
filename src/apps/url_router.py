from django.urls import include, path

app_name = 'url_router'

urlpatterns =[
    path('auth/', include('apps.account.api.urls', namespace='account')),
    path('analytics/', include('apps.analytics.api.urls', namespace='analytics')),
    path('shortener/', include('apps.shortener.api.urls', namespace='shortener')),
]