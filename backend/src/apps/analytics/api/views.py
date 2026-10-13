from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.db.models import Count, F, Min
from django.db.models.functions import ExtractHour, TruncDate
from django.utils import timezone
from rest_framework import viewsets
from django_filters import rest_framework as filters
from rest_framework.response import Response

from apps.analytics.api.filters import URLClickFilterSet
from apps.analytics.api.serializers import AnalyticsQuerySerializer, URLClickSerializer
from apps.analytics.models import URLClick
from apps.shortener.models import URL
from core.api.views import BaseAPIView, BaseAPIViewSet


class URLClickViewSet(BaseAPIViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = URLClick.objects.select_related('short_url__url').order_by('-created_at')
    serializer_class = URLClickSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = URLClickFilterSet
    user_field = 'short_url__url__user'


class AnalyticsSummaryView(BaseAPIView):
    """
    Click analytics over the last `days` days (today included), for all of the
    user's links or scoped to one link, collection or tag. Days are bucketed in
    the requested time zone. Bot clicks (link previews, crawlers) are only counted
    in `totals.bots`.
    """
    user_field = None

    def get(self, request):
        query = AnalyticsQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        params = query.validated_data
        days, tz = params['days'], ZoneInfo(params['tz'])

        links = URL.objects.filter(user=request.user)
        if 'url' in params:
            links = links.filter(pk=params['url'])
        if 'collection' in params:
            links = links.filter(collection_id=params['collection'])
        if 'tag' in params:
            links = links.filter(tags=params['tag'])

        clicks = URLClick.objects.filter(short_url__url__in=links)
        today = timezone.now().astimezone(tz).date()
        first_day = today - timedelta(days=days - 1)
        start = datetime.combine(first_day, time.min, tzinfo=tz)
        human = clicks.filter(is_bot=False)
        current = human.filter(created_at__gte=start)

        per_day = dict(
            current.annotate(day=TruncDate('created_at', tzinfo=tz)).values('day')
            .annotate(n=Count('id')).values_list('day', 'n')
        )
        per_hour = dict(
            current.annotate(hour=ExtractHour('created_at', tzinfo=tz)).values('hour')
            .annotate(n=Count('id')).values_list('hour', 'n')
        )

        def breakdown(field, limit=6):
            rows = current.values(field).annotate(clicks=Count('id')).order_by('-clicks', field)[:limit]
            return [{'name': row[field] or None, 'clicks': row['clicks']} for row in rows]

        top_links = [
            {'id': row['link_id'], 'name': row['link_name'], 'url': row['link_url'], 'code': row['code'],
             'clicks': row['clicks']}
            for row in current.values(
                link_id=F('short_url__url_id'), link_name=F('short_url__url__name'), link_url=F('short_url__url__url'),
            ).annotate(code=Min('short_url__short_url'), clicks=Count('id')).order_by('-clicks', 'link_id')[:5]
        ]

        return Response({
            'range': {
                'days': days,
                'start': first_day.isoformat(),
                'end': today.isoformat(),
                'timezone': params['tz'],
            },
            'totals': {
                'clicks': current.count(),
                'previous_clicks': human.filter(
                    created_at__gte=start - timedelta(days=days), created_at__lt=start,
                ).count(),
                'visitors': current.order_by().values('ipv4_address', 'ipv6_address').distinct().count(),
                'bots': clicks.filter(is_bot=True, created_at__gte=start).count(),
                'links': links.count(),
            },
            'series': [
                {'date': day.isoformat(), 'clicks': per_day.get(day, 0)}
                for day in (first_day + timedelta(days=i) for i in range(days))
            ],
            'hours': [per_hour.get(hour, 0) for hour in range(24)],
            'top_links': top_links,
            # Every link clicked in the range, for maps that size each link by its clicks
            'link_clicks': [
                {'id': link_id, 'clicks': n}
                for link_id, n in current.values_list('short_url__url_id').annotate(n=Count('id')).order_by('-n')
            ],
            'referrers': breakdown('referer_domain', limit=8),
            'browsers': breakdown('browser'),
            'os': breakdown('os'),
            'devices': breakdown('device'),
        })
