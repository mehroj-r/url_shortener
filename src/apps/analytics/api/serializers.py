from rest_framework import serializers

from apps.analytics.models import URLClick


class URLClickSerializer(serializers.ModelSerializer):

    class Meta:
        model = URLClick
        fields = ['id', 'short_url',  'ipv4_address', 'ipv6_address', 'user_agent']
        read_only_fields = ['id', 'created_at', 'updated_at']