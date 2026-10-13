from django.db.models import Exists, OuterRef, Q
from django.utils import timezone
from django_filters import rest_framework as filters

from apps.shortener.models import URL, ShortURL


class URLFilterSet(filters.FilterSet):
    collection = filters.CharFilter(method='filter_collection', help_text="Collection id, or 'none'.")
    tag = filters.NumberFilter(field_name='tags', lookup_expr='exact')
    status = filters.ChoiceFilter(
        method='filter_status',
        choices=[('active', 'Active'), ('expired', 'Expired'), ('inactive', 'Inactive')],
    )

    class Meta:
        model = URL
        fields = ['collection', 'tag', 'status']

    def filter_collection(self, queryset, name, value):
        if value == 'none':
            return queryset.filter(collection__isnull=True)
        if not value.isdigit():
            return queryset.none()
        return queryset.filter(collection_id=value)

    def filter_status(self, queryset, name, value):
        now = timezone.now()
        codes = ShortURL.objects.filter(url=OuterRef('pk'), is_active=True)
        live = Exists(codes.filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now)))
        expired = Exists(codes.filter(expires_at__lte=now))
        if value == 'active':
            return queryset.filter(live)
        if value == 'expired':
            return queryset.filter(~live, expired)
        return queryset.filter(~live, ~expired)
