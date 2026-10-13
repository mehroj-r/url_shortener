from zoneinfo import available_timezones

from django.conf import settings
from rest_framework import serializers

from apps.analytics.models import URLClick


class URLClickSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source='short_url.short_url', read_only=True)
    link = serializers.IntegerField(source='short_url.url_id', read_only=True)
    link_name = serializers.CharField(source='short_url.url.name', read_only=True)

    class Meta:
        model = URLClick
        fields = ['id', 'short_url', 'code', 'link', 'link_name', 'ipv4_address', 'ipv6_address', 'user_agent',
                  'referer', 'referer_domain', 'browser', 'os', 'device', 'is_bot', 'created_at']
        read_only_fields = fields


class AnalyticsQuerySerializer(serializers.Serializer):
    days = serializers.IntegerField(min_value=1, max_value=365, default=30)
    url = serializers.IntegerField(required=False)
    collection = serializers.IntegerField(required=False)
    tag = serializers.IntegerField(required=False)
    tz = serializers.CharField(default=settings.TIME_ZONE)

    def validate_tz(self, value):
        if value not in available_timezones():
            raise serializers.ValidationError("Unknown time zone.")
        return value
