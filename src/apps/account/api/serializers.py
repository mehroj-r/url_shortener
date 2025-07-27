from django.contrib.auth import get_user_model
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

    def validate(self, attrs):

        # Check if the password and password_repeat match
        if attrs['password'] != attrs['password_repeat']:
            raise serializers.ValidationError({
                "password": _("Passwords do not match."),
                "password_repeat": _("Passwords do not match.")
            })
        else:
            # Remove password_repeat from attrs as it's not needed for saving
            attrs.pop('password_repeat')

        return super().validate(attrs)


class LoginSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login_fields = get_user_model().LOGIN_FIELDS  # noqa

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

        # Build query for user lookup
        query_params = { }
        for field, value in provided_login_fields.items():
            query_params[field] = value

        try:
            user = User.objects.get(**query_params)

            # Validate password
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError({
                    "password": _("Incorrect password.")
                })

            # Store user in validated_data for later use
            attrs['user'] = user
            return attrs

        except User.DoesNotExist:
            raise serializers.ValidationError({
                "credentials": _("No active account found with the provided credentials.")
            })

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