from django_filters import rest_framework as filters

from apps.analytics.models import URLClick


class URLClickFilterSet(filters.FilterSet):
    short_url_id = filters.NumberFilter(field_name='short_url', lookup_expr='exact')
    url_id = filters.NumberFilter(field_name='short_url__url', lookup_expr='exact')

    class Meta:
        model = URLClick
        fields = ['short_url']