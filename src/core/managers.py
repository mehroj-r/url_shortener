from django.db.models import Manager

class SoftDeleteManager(Manager):
    """Manager that filters out soft-deleted objects by default."""

    def get_queryset(self):
        """Return NOT DELETED objects."""
        return super().get_queryset().filter(deleted_at__isnull=True)

    def deleted(self):
        """Return DELETED objects."""
        return super().get_queryset().filter(deleted_at__isnull=False)

    def with_deleted(self):
        """Return ALL objects."""
        return super().get_queryset()