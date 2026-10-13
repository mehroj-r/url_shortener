import secrets
import string

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shortener.validators import validate_short_code_format, validate_short_code_not_reserved
from core.models import TimestampedModel, SoftDeleteModel


class URLCollection(TimestampedModel, SoftDeleteModel):

    name = models.CharField(
        max_length=255,
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

    class Meta:
        verbose_name = _("Short URL")
        verbose_name_plural = _("Short URLs")

    def __str__(self):
        return f"{self.url.name} ({self.short_url})"

    @classmethod
    def generate_code(cls) -> str:
        """Return a random short code that has never been used."""
        while True:
            code = ''.join(secrets.choice(cls.CODE_ALPHABET) for _position in range(cls.CODE_LENGTH))
            if not cls.all_objects.filter(short_url=code).exists():
                return code
