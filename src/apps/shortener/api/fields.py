from rest_framework import serializers


class OwnedPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """Primary key field that only accepts objects owned by the requesting user."""

    def __init__(self, user_field='user', **kwargs):
        self.user_field = user_field
        super().__init__(**kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(**{self.user_field: self.context['request'].user})
