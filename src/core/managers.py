from django.db import transaction
from django.db.models import CASCADE, Manager, QuerySet
from django.utils import timezone


def _is_soft_deletable(model) -> bool:
    return any(field.name == 'deleted_at' for field in model._meta.concrete_fields)


def _cascading_soft_deletable_relations(model):
    """Yield the reverse relations whose rows CASCADE from `model` and can themselves be soft deleted."""
    for relation in model._meta.related_objects:
        if relation.on_delete is CASCADE and _is_soft_deletable(relation.related_model):
            yield relation


def soft_delete_queryset(queryset: QuerySet, deleted_at) -> int:
    """
    Mark the live rows of `queryset` as deleted, after doing the same for every live
    row that CASCADEs from them. Each level is a single UPDATE, so the cost does not
    grow with the number of related rows.

    Relations that are not CASCADE, or point at models without `deleted_at`, are left
    alone: the soft-deleted parent row still exists, so their foreign keys stay valid.
    """
    live = queryset.model._base_manager.filter(pk__in=queryset.values('pk'), deleted_at__isnull=True)

    for relation in _cascading_soft_deletable_relations(queryset.model):
        children = relation.related_model._base_manager.filter(**{f'{relation.field.name}__in': live.values('pk')})
        soft_delete_queryset(children, deleted_at)

    return live.update(deleted_at=deleted_at)


def restore_queryset(queryset: QuerySet, deleted_at) -> int:
    """Restore the rows of `queryset`, and their CASCADE children, that were deleted at `deleted_at`."""
    deleted = queryset.model._base_manager.filter(pk__in=queryset.values('pk'), deleted_at=deleted_at)

    for relation in _cascading_soft_deletable_relations(queryset.model):
        children = relation.related_model._base_manager.filter(**{f'{relation.field.name}__in': deleted.values('pk')})
        restore_queryset(children, deleted_at)

    return deleted.update(deleted_at=None)


class SoftDeleteQuerySet(QuerySet):
    """QuerySet whose delete() soft deletes, so bulk deletes (e.g. the admin action) keep the data."""

    def delete(self):
        with transaction.atomic(using=self.db):
            count = soft_delete_queryset(self, timezone.now())
        return count, {self.model._meta.label: count}

    delete.alters_data = True
    delete.queryset_only = True

    def hard_delete(self):
        return super().delete()

    hard_delete.alters_data = True
    hard_delete.queryset_only = True


class SoftDeleteManager(Manager.from_queryset(SoftDeleteQuerySet)):
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
