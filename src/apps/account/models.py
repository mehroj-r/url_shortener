from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from core.models import TimestampedModel, SoftDeleteModel
from django.contrib.auth.hashers import make_password

from apps.account import managers


class User(AbstractBaseUser, TimestampedModel, SoftDeleteModel):

    first_name = models.CharField(max_length=30, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=30, verbose_name=_('Last Name'))

    username = models.CharField(
        max_length=150,
        verbose_name=_('Username'),
        null=True,
    )

    phone = PhoneNumberField(
        max_length=15,
        unique=True,
        verbose_name=_('Phone Number'),
        null=True,
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

    def save(self, *args, **kwargs):

        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password) # Hash the password

        return super().save(*args, **kwargs)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def has_module_perms(self, app_label):
        return self.is_staff and self.is_active and self.is_superuser and not self.deleted_at

    def has_perm(self, perm, obj=None):
        return self.is_staff and self.is_active and self.is_superuser and not self.deleted_at