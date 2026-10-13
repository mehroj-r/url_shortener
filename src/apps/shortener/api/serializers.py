from rest_framework import serializers

from django.utils.translation import gettext_lazy as _
from rest_framework.fields import CurrentUserDefault
from rest_framework.validators import UniqueValidator

from apps.shortener.api.fields import OwnedPrimaryKeyRelatedField
from apps.shortener.models import URL, URLCollection, ShortURL


class URLSerializer(serializers.ModelSerializer):

    user = serializers.HiddenField(default=CurrentUserDefault())
    collection = OwnedPrimaryKeyRelatedField(queryset=URLCollection.objects.all(), required=False, allow_null=True)
    allowed_prefixes = ('http://', 'https://') # noqa

    class Meta:
        model = URL
        fields = ['id', 'name', 'url', 'user', 'collection', 'created_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_url(self, value):
        if not value.startswith(self.allowed_prefixes):
            raise serializers.ValidationError(
                _("URL must start with any of the following prefixes: {}").format(",".join(self.allowed_prefixes))
            )
        return value

class URLNestedSerializer(URLSerializer):
    """The collection comes from the URL path (see URLNestedViewSet)."""
    collection = serializers.PrimaryKeyRelatedField(read_only=True)


class URLCollectionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = URLCollection
        fields = ['id', 'name', 'user', 'created_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        # Names are unique per user (see the model constraint)
        collections = URLCollection.objects.filter(user=self.context['request'].user, name=value)
        if self.instance is not None:
            collections = collections.exclude(pk=self.instance.pk)
        if collections.exists():
            raise serializers.ValidationError(_("You already have a collection with this name."))
        return value


class ShortURLSerializer(serializers.ModelSerializer):
    url = OwnedPrimaryKeyRelatedField(queryset=URL.objects.all())

    class Meta:
        model = ShortURL
        fields = ['id', 'url', 'short_url', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            # Optional: a random code is generated when omitted.
            # Uniqueness includes soft-deleted codes, which are never reused.
            'short_url': {
                'required': False,
                'max_length': 64,
                'validators': [
                    *ShortURL._meta.get_field('short_url').validators,
                    UniqueValidator(queryset=ShortURL.all_objects.all()),
                ],
            },
        }

    def create(self, validated_data):
        validated_data.setdefault('short_url', ShortURL.generate_code())
        return super().create(validated_data)


class ShortURLNestedSerializer(ShortURLSerializer):
    """The URL comes from the URL path (see ShortURLNestedViewSet)."""
    url = serializers.PrimaryKeyRelatedField(read_only=True)
