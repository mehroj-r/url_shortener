from django.contrib.auth.base_user import BaseUserManager

from core.managers import SoftDeleteManager


class UserManager(SoftDeleteManager, BaseUserManager):
    """User manager that hides soft-deleted users, so they can't authenticate."""

    def get_by_natural_key(self, email):
        """ Returns the user with the given email (case-insensitive)."""
        return self.get(**{f'{self.model.USERNAME_FIELD}__iexact': email })

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and returns a user with an email and password.
        """
        if not email:
            raise ValueError('The given email must be set')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and returns a superuser with an email and password.
        """
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True

        return self.create_user(email, password, **extra_fields)
