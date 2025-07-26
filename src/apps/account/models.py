from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from core.models import TimestampedModel, SoftDeleteModel
from django.contrib.auth.hashers import make_password

from apps.account import managers


class User(AbstractBaseUser, TimestampedModel, SoftDeleteModel):

    first_name = models.CharField(max_length=30, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=30, verbose_name=_('Last Name'))

    phone = PhoneNumberField(
        max_length=15,
        unique=True,
        verbose_name=_('Phone Number'),
        null=True,
        blank=True,
    )

    email = models.EmailField(
        unique=True,
        verbose_name=_('Email'),
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    # For Django Admin
    is_staff = models.BooleanField(default=False, verbose_name=_('Is staff'))
    is_superuser = models.BooleanField(default=False, verbose_name=_('Is superuser'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))

    objects = managers.UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.get_full_name()

    def save(self, *args, **kwargs):

        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password) # Hash the password

        return super().save(*args, **kwargs)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"