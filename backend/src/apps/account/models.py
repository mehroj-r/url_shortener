import secrets
from datetime import timedelta

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils import timezone
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from core.models import TimestampedModel, SoftDeleteModel

from apps.account import managers


class User(AbstractBaseUser, TimestampedModel, SoftDeleteModel):

    first_name = models.CharField(max_length=30, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=30, verbose_name=_('Last Name'))

    username = models.CharField(
        max_length=150,
        verbose_name=_('Username'),
        null=True,
        blank=True,
    )

    phone = PhoneNumberField(
        max_length=15,
        unique=True,
        verbose_name=_('Phone Number'),
        null=True,
        blank=True,
    )

    email = models.EmailField(
        verbose_name=_('Email'),
        unique=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    LOGIN_FIELDS = ['email', 'username', 'phone']

    # For Django Admin
    is_staff = models.BooleanField(default=False, verbose_name=_('Is staff'))
    is_superuser = models.BooleanField(default=False, verbose_name=_('Is superuser'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))

    objects = managers.UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        constraints = [
            models.UniqueConstraint(
                Lower('email'),
                name='unique_email_constraint'
            ),
            models.UniqueConstraint(
                Lower('username'),
                name='unique_username_constraint'
            ),
        ]

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def has_module_perms(self, app_label):
        return self.is_staff and self.is_active and self.is_superuser and not self.deleted_at

    def has_perm(self, perm, obj=None):
        return self.is_staff and self.is_active and self.is_superuser and not self.deleted_at


INVITE_LIFETIME = timedelta(days=7)


def generate_invite_token():
    return secrets.token_urlsafe(16)


def default_invite_expiry():
    return timezone.now() + INVITE_LIFETIME


class Invite(TimestampedModel):
    """A single-use invitation to create an account."""

    token = models.CharField(
        max_length=64,
        unique=True,
        default=generate_invite_token,
        editable=False,
        verbose_name=_('Token'),
    )
    note = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_('Note'),
        help_text=_('Who the invite is for; only visible to its creator.'),
    )
    created_by = models.ForeignKey(
        'account.User',     # noqa
        on_delete=models.CASCADE,
        related_name='invites_sent',
    )
    used_by = models.OneToOneField(
        'account.User',     # noqa
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invite',
    )
    used_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Used At'))
    expires_at = models.DateTimeField(default=default_invite_expiry, verbose_name=_('Expires At'))

    class Meta:
        verbose_name = _('Invite')
        verbose_name_plural = _('Invites')

    def __str__(self):
        return f"Invite by {self.created_by_id} ({self.status})"

    @property
    def status(self) -> str:
        if self.used_at is not None:
            return 'used'
        if self.expires_at <= timezone.now():
            return 'expired'
        return 'pending'
