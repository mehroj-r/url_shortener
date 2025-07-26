from django.db import models

from core.models import TimestampedModel, SoftDeleteModel


class URLClick(TimestampedModel, SoftDeleteModel):

    url = models.ForeignKey(
        "shortener.URL",  # noqa
        on_delete=models.CASCADE,
        related_name='clicks',
    )
    ipv4_address = models.GenericIPAddressField(
        protocol='IPv4',
        null=True,
        blank=True,
    )
    ipv6_address = models.GenericIPAddressField(
        protocol='IPv6',
        null=True,
        blank=True,
    )
    user_agent = models.CharField(
        max_length=512,
        null=True,
        blank=True,
    )
    referer = models.URLField(
        max_length=2048,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "URL Info"
        verbose_name_plural = "URL Infos"

    def __str__(self):
        return self.url
