from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):

    def get_by_natural_key(self, email):
        """ Returns the user with the given phone number."""
        return self.get(**{self.model.USERNAME_FIELD: email })

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and returns a user with an email, phone, and password.
        """
        if not email:
            raise ValueError('The given phone must be set')

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and returns a superuser with an email, phone, and password.
        """
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True

        return self.create_user(email, password, **extra_fields)
