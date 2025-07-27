from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, SoftDeleteModel


class URLCollection(TimestampedModel, SoftDeleteModel):

    name = models.CharField(
        max_length=255,
        unique=True,
    )
    user = models.ForeignKey(
        'account.User',     # noqa
        on_delete=models.CASCADE,
        related_name='url_collections',
    )

    class Meta:
        verbose_name = _("URL Collection")
        verbose_name_plural = _("URL Collections")

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

    url = models.ForeignKey(
        "shortener.URL", # noqa
        on_delete=models.CASCADE,
        related_name='short_urls',
    )
    short_url = models.CharField(
        max_length=255,
        unique=True,
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
