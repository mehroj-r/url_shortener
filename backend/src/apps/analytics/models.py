from django.db import models

from core.models import TimestampedModel, SoftDeleteModel


class URLClick(TimestampedModel, SoftDeleteModel):

    short_url = models.ForeignKey(
        "shortener.ShortURL",  # noqa
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

    # Parsed when the click is recorded (see analytics.user_agents)
    referer_domain = models.CharField(max_length=255, null=True, blank=True)
    browser = models.CharField(max_length=64, blank=True, default='')
    os = models.CharField(max_length=64, blank=True, default='')
    device = models.CharField(
        max_length=16,
        choices=[
            ('desktop', 'Desktop'), ('mobile', 'Mobile'), ('tablet', 'Tablet'), ('bot', 'Bot'), ('other', 'Other'),
        ],
        default='other',
    )
    is_bot = models.BooleanField(
        default=False,
        help_text="Link previews and crawlers; excluded from analytics.",
    )

    class Meta:
        verbose_name = "URL Info"
        verbose_name_plural = "URL Infos"
        indexes = [
            models.Index(fields=['short_url', 'created_at'], name='urlclick_short_url_created'),
            models.Index(fields=['created_at'], name='urlclick_created'),
        ]

    def __str__(self):
        return f"{self.short_url_id} @ {self.created_at:%Y-%m-%d %H:%M:%S}"
