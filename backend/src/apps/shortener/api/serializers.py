from django.db import transaction
from django.db.models.functions import Lower
from django.utils import timezone
from rest_framework import serializers

from django.utils.translation import gettext_lazy as _
from rest_framework.fields import CurrentUserDefault
from rest_framework.validators import UniqueValidator

from apps.shortener.api.fields import OwnedPrimaryKeyRelatedField
from apps.shortener.models import LINE_COLORS, URL, URLCollection, ShortURL, Tag

SHORT_CODE_VALIDATORS = [
    *ShortURL._meta.get_field('short_url').validators,
    # Includes soft-deleted codes, which are never reused
    UniqueValidator(queryset=ShortURL.all_objects.all(), message=_("This short code is already taken.")),
]


def validate_future(value):
    if value is not None and value <= timezone.now():
        raise serializers.ValidationError(_("Expiry must be in the future."))
    return value


class ShortCodeSummarySerializer(serializers.ModelSerializer):
    """A link's short code as listed on the link itself."""
    clicks = serializers.IntegerField(source='click_count', read_only=True, default=0)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = ShortURL
        fields = ['id', 'short_url', 'is_active', 'expires_at', 'status', 'clicks', 'created_at']


class URLSerializer(serializers.ModelSerializer):

    user = serializers.HiddenField(default=CurrentUserDefault())
    collection = OwnedPrimaryKeyRelatedField(queryset=URLCollection.objects.all(), required=False, allow_null=True)
    tags = OwnedPrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)
    short_urls = ShortCodeSummarySerializer(many=True, read_only=True)
    clicks = serializers.IntegerField(read_only=True, default=0)
    last_clicked_at = serializers.DateTimeField(read_only=True, default=None)
    status = serializers.SerializerMethodField()

    # Create only: the link's first short code (generated when omitted) and its expiry
    code = serializers.CharField(
        source='short_url', write_only=True, required=False, allow_blank=True, max_length=64,
        validators=SHORT_CODE_VALIDATORS,
    )
    expires_at = serializers.DateTimeField(write_only=True, required=False, allow_null=True,
                                           validators=[validate_future])
    allowed_prefixes = ('http://', 'https://') # noqa

    class Meta:
        model = URL
        fields = ['id', 'name', 'url', 'user', 'collection', 'tags', 'short_urls', 'clicks', 'last_clicked_at',
                  'status', 'code', 'expires_at', 'created_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_url(self, value):
        if not value.startswith(self.allowed_prefixes):
            raise serializers.ValidationError(
                _("URL must start with any of the following prefixes: {}").format(",".join(self.allowed_prefixes))
            )
        return value

    def get_status(self, link) -> str:
        statuses = {code.status for code in link.short_urls.all()}
        if 'active' in statuses:
            return 'active'
        return 'expired' if 'expired' in statuses else 'inactive'

    def create(self, validated_data):
        code = validated_data.pop('short_url', None) or ShortURL.generate_code()
        expires_at = validated_data.pop('expires_at', None)
        with transaction.atomic():
            link = super().create(validated_data)
            ShortURL.objects.create(url=link, short_url=code, expires_at=expires_at)
        return link

    def update(self, instance, validated_data):
        validated_data.pop('short_url', None)
        validated_data.pop('expires_at', None)
        return super().update(instance, validated_data)


class URLNestedSerializer(URLSerializer):
    """The collection comes from the URL path (see URLNestedViewSet)."""
    collection = serializers.PrimaryKeyRelatedField(read_only=True)


class BulkLinkActionSerializer(serializers.Serializer):
    ACTIONS = ['delete', 'move', 'add_tag', 'remove_tag', 'activate', 'deactivate']

    ids = serializers.ListField(child=serializers.IntegerField(), min_length=1, max_length=500)
    action = serializers.ChoiceField(choices=ACTIONS)
    collection = OwnedPrimaryKeyRelatedField(queryset=URLCollection.objects.all(), required=False, allow_null=True)
    tag = OwnedPrimaryKeyRelatedField(queryset=Tag.objects.all(), required=False)

    def validate(self, attrs):
        if attrs['action'] == 'move' and 'collection' not in attrs:
            raise serializers.ValidationError({'collection': _("Choose a collection, or null for none.")})
        if attrs['action'] in ('add_tag', 'remove_tag') and 'tag' not in attrs:
            raise serializers.ValidationError({'tag': _("Choose a tag.")})
        return attrs


class URLCollectionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    link_count = serializers.IntegerField(read_only=True, default=0)
    clicks = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = URLCollection
        fields = ['id', 'name', 'color', 'user', 'link_count', 'clicks', 'created_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'color': {'required': False}}

    def create(self, validated_data):
        if 'color' not in validated_data:
            # The next line colour in order, so a new collection rarely repeats a colour
            count = URLCollection.objects.filter(user=validated_data['user']).count()
            validated_data['color'] = LINE_COLORS[count % len(LINE_COLORS)]
        return super().create(validated_data)

    def validate_name(self, value):
        # Names are unique per user (see the model constraint)
        collections = URLCollection.objects.filter(user=self.context['request'].user, name=value)
        if self.instance is not None:
            collections = collections.exclude(pk=self.instance.pk)
        if collections.exists():
            raise serializers.ValidationError(_("You already have a collection with this name."))
        return value


class TagSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    link_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'user', 'link_count', 'created_at']
        read_only_fields = ['id', 'created_at']
        validators = []

    def validate_name(self, value):
        # Unique per user, ignoring case (see the model constraint)
        tags = Tag.objects.annotate(lower_name=Lower('name')).filter(
            user=self.context['request'].user, lower_name=value.lower()
        )
        if self.instance is not None:
            tags = tags.exclude(pk=self.instance.pk)
        if tags.exists():
            raise serializers.ValidationError(_("You already have a tag with this name."))
        return value


class ShortURLSerializer(serializers.ModelSerializer):
    url = OwnedPrimaryKeyRelatedField(queryset=URL.objects.all())
    clicks = serializers.IntegerField(source='click_count', read_only=True, default=0)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = ShortURL
        fields = ['id', 'url', 'short_url', 'is_active', 'expires_at', 'status', 'clicks', 'created_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            # Optional: a random code is generated when omitted.
            'short_url': {
                'required': False,
                'max_length': 64,
                'validators': SHORT_CODE_VALIDATORS,
            },
            'expires_at': {'validators': [validate_future]},
        }

    def create(self, validated_data):
        validated_data.setdefault('short_url', ShortURL.generate_code())
        return super().create(validated_data)


class ShortURLNestedSerializer(ShortURLSerializer):
    """The URL comes from the URL path (see ShortURLNestedViewSet)."""
    url = serializers.PrimaryKeyRelatedField(read_only=True)
