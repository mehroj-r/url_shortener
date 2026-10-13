from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.account.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True)
    password_repeat = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'phone',
            'email',
            'password',
            'password_repeat',
        )
        # Uniqueness is checked below: case-insensitively, and including soft-deleted users
        extra_kwargs = {
            'username': {'validators': []},
            'phone': {'validators': []},
            'email': {'validators': []},
        }

    @staticmethod
    def _check_unique(field, lookup, value):
        if value and User.all_objects.filter(**{lookup: value}).exists():
            raise serializers.ValidationError(_("A user with this {} already exists.").format(field))
        return value

    def validate_email(self, value):
        return self._check_unique('email', 'email__iexact', value)

    def validate_username(self, value):
        return self._check_unique('username', 'username__iexact', value)

    def validate_phone(self, value):
        return self._check_unique('phone number', 'phone', value)

    def validate(self, attrs):

        # Check if the password and password_repeat match
        if attrs['password'] != attrs['password_repeat']:
            raise serializers.ValidationError({
                "password": _("Passwords do not match."),
                "password_repeat": _("Passwords do not match.")
            })

        # Remove password_repeat from attrs as it's not needed for saving
        attrs.pop('password_repeat')

        # Run AUTH_PASSWORD_VALIDATORS against the would-be user
        user = User(**{key: value for key, value in attrs.items() if key != 'password'})
        try:
            validate_password(attrs['password'], user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)}) from e

        return super().validate(attrs)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login_fields = User.LOGIN_FIELDS

        # Dynamically add login fields to the serializer
        for field in self.login_fields:
            field_class = serializers.EmailField if field == 'email' else serializers.CharField
            self.fields[field] = field_class(write_only=True, required=False)

    def validate(self, attrs):
        # Check if at least one login field is provided
        provided_login_fields = { field: attrs.get(field) for field in self.login_fields if attrs.get(field) }

        # If no login fields are provided, raise a validation error
        if not provided_login_fields:
            raise serializers.ValidationError({
                "login": _("At least one of the following fields must be provided: {}").format(
                    ", ".join(self.login_fields)
                )
            })

        # Ensure that only one login field is provided
        if len(provided_login_fields) > 1:
            raise serializers.ValidationError({
                "login": _("Only one of the following fields can be provided: {}").format(
                    ", ".join(self.login_fields)
                )
            })

        # Email and username are unique case-insensitively, so look them up the same way
        field, value = next(iter(provided_login_fields.items()))
        lookup = field if field == 'phone' else f'{field}__iexact'
        user = User.objects.filter(**{lookup: value}).first()

        if user is None:
            # Hash anyway, so response time doesn't reveal whether the account exists
            User().set_password(attrs['password'])

        # One error for every failure, so responses don't reveal whether the account exists
        if user is None or not user.check_password(attrs['password']) or not user.is_active:
            raise serializers.ValidationError({
                "credentials": _("No active account found with the provided credentials.")
            })

        # Store user in validated_data for later use
        attrs['user'] = user
        return attrs

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        user = instance.get('user', None)

        if not user:
            return {}

        refresh = RefreshToken.for_user(user)

        ret['user'] = UserRegistrationSerializer(user).data
        ret['token'] = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return ret
