from django_filters import rest_framework as filters

from apps.analytics.models import URLClick


class URLClickFilterSet(filters.FilterSet):
    short_url_id = filters.NumberFilter(field_name='short_url', lookup_expr='exact')
    url_id = filters.NumberFilter(field_name='short_url__url', lookup_expr='exact')
    collection = filters.NumberFilter(field_name='short_url__url__collection', lookup_expr='exact')
    is_bot = filters.BooleanFilter(field_name='is_bot')

    class Meta:
        model = URLClick
        fields = ['short_url']
