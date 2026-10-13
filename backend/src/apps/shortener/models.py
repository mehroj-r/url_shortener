import secrets
import string

from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.shortener.validators import validate_short_code_format, validate_short_code_not_reserved
from core.models import TimestampedModel, SoftDeleteModel


# Identity colours for collections and tags, in the fixed order new collections take them.
# The frontend maps each name to a colour-vision-checked hue.
LINE_COLORS = ['red', 'blue', 'green', 'violet', 'amber', 'teal']
LINE_COLOR_CHOICES = [(color, color.title()) for color in LINE_COLORS]


class URLCollection(TimestampedModel, SoftDeleteModel):

    name = models.CharField(
        max_length=255,
    )
    color = models.CharField(
        max_length=16,
        choices=LINE_COLOR_CHOICES,
        default='red',
    )
    user = models.ForeignKey(
        'account.User',     # noqa
        on_delete=models.CASCADE,
        related_name='url_collections',
    )

    class Meta:
        verbose_name = _("URL Collection")
        verbose_name_plural = _("URL Collections")
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                condition=models.Q(deleted_at__isnull=True),
                name='unique_collection_name_per_user',
                violation_error_message=_("You already have a collection with this name."),
            ),
        ]

    def __str__(self):
        return self.name


class Tag(TimestampedModel):

    COLOR_CHOICES = [('slate', 'Slate'), *LINE_COLOR_CHOICES]

    user = models.ForeignKey(
        'account.User',     # noqa
        on_delete=models.CASCADE,
        related_name='tags',
    )
    name = models.CharField(
        max_length=50,
    )
    color = models.CharField(
        max_length=16,
        choices=COLOR_CHOICES,
        default='slate',
    )

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        constraints = [
            models.UniqueConstraint(
                'user',
                Lower('name'),
                name='unique_tag_name_per_user',
                violation_error_message=_("You already have a tag with this name."),
            ),
        ]

    def __str__(self):
        return self.name


class URL(TimestampedModel, SoftDeleteModel):

    name = models.CharField(
        max_length=255,
    )
    url = models.URLField(
        max_length=2048
    )
    collection = models.ForeignKey(
        "shortener.URLCollection",      # noqa
        on_delete=models.CASCADE,
        related_name='urls',
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        "account.User",         # noqa
        on_delete=models.CASCADE,
        related_name='urls',
    )
    tags = models.ManyToManyField(
        "shortener.Tag",        # noqa
        related_name='urls',
        blank=True,
    )

    class Meta:
        verbose_name = _("URL")
        verbose_name_plural = _("URLs")

    def __str__(self):
        return f"{self.url} ({self.collection.name if self.collection else "default"})"


class ShortURL(TimestampedModel, SoftDeleteModel):

    CODE_ALPHABET = string.ascii_letters + string.digits
    CODE_LENGTH = 7

    url = models.ForeignKey(
        "shortener.URL", # noqa
        on_delete=models.CASCADE,
        related_name='short_urls',
    )
    # Unique across soft-deleted rows too: a code is never reused, so old shared links can't be taken over
    short_url = models.CharField(
        max_length=255,
        unique=True,
        validators=[validate_short_code_format, validate_short_code_not_reserved],
        help_text=_("The short version of the URL."),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Indicates whether the short URL is active or not."),
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("After this moment the short URL stops redirecting."),
    )

    class Meta:
        verbose_name = _("Short URL")
        verbose_name_plural = _("Short URLs")

    def __str__(self):
        return f"{self.url.name} ({self.short_url})"

    @property
    def status(self) -> str:
        if not self.is_active:
            return 'inactive'
        if self.expires_at is not None and self.expires_at <= timezone.now():
            return 'expired'
        return 'active'

    @classmethod
    def generate_code(cls) -> str:
        """Return a random short code that has never been used."""
        while True:
            code = ''.join(secrets.choice(cls.CODE_ALPHABET) for _position in range(cls.CODE_LENGTH))
            if not cls.all_objects.filter(short_url=code).exists():
                return code
