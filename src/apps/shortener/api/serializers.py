from rest_framework import serializers

from django.utils.translation import gettext_lazy as _
from rest_framework.fields import CurrentUserDefault

from apps.shortener.api.defaults import CurrentCollectionDefault
from apps.shortener.models import URL, URLCollection, ShortURL


class URLSerializer(serializers.ModelSerializer):

    user = serializers.HiddenField(default=CurrentUserDefault())
    allowed_prefixes = ('http://', 'https://') # noqa

    class Meta:
        model = URL
        fields = ['id', 'name', 'url', 'user', 'collection', 'created_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_url(self, value):
        if not value.startswith(self.allowed_prefixes):
            raise serializers.ValidationError(_(f"URL must start with any of the following prefixes: {",".join(self.allowed_prefixes)}"))
        return value

class URLNestedSerializer(URLSerializer):
    collection = serializers.HiddenField(default=CurrentCollectionDefault())

    class Meta(URLSerializer.Meta):
        fields = URLSerializer.Meta.fields + ['collection']
        read_only_fields = URLSerializer.Meta.read_only_fields + ['collection']


class URLCollectionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = URLCollection
        fields = ['id', 'name', 'user', 'created_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ShortURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortURL
        fields = ['id', 'url', 'short_url', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at', 'updated_at']