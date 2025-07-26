from django.db import models

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
        verbose_name = "URL Collection"
        verbose_name_plural = "URL Collections"

    def __str__(self):
        return self.name

class URL(TimestampedModel, SoftDeleteModel):

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="A unique name for the URL, used for easy identification.",
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

    class Meta:
        verbose_name = "URL"
        verbose_name_plural = "URLs"

    def __str__(self):
        return f"{self.url} ({self.collection.name if self.collection else "default"})"