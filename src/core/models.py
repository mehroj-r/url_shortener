from functools import reduce
from operator import or_
from typing import List, Optional

from django.db import models, router, transaction
from django.db.models.deletion import CASCADE, Collector
from django.db.models.fields.reverse_related import ForeignObjectRel
from django.db.models.query import QuerySet
from django.db.models.sql.subqueries import UpdateQuery
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from core.managers import SoftDeleteManager


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        abstract = True


def SOFT_DELETE_CASCADE(collector: Collector, field: ForeignObjectRel, sub_objs: QuerySet, using: str) -> None:
    """
    Custom CASCADE function that only marks objects for soft delete
    without recursive collection.

    Args:
        collector: The Django collector instance
        field: The field relationship being processed
        sub_objs: The QuerySet containing objects to process
        using: The database alias to use
    """
    if not hasattr(collector, "soft_deletes"):
        collector.soft_deletes = []

    collector.soft_deletes.extend(list(sub_objs))

class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('Deleted At')
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    @property
    def is_deleted(self) -> bool:
        """Return whether the object is soft-deleted."""
        return self.deleted_at is not None

    def delete(self, using: Optional[str] = None, keep_parents: bool = False) -> None:
        """
        Soft delete the object by setting the deleted_at timestamp.
        """
        self._perform_on_delete(using=using, keep_parents=keep_parents)
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def hard_delete(self, using: Optional[str] = None, keep_parents: bool = False) -> None:
        """
        Permanently delete the object from the database.
        """
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self) -> None:
        """
        Restore a soft-deleted object by clearing the deleted_at timestamp.
        """
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    class Meta:
        abstract = True

    def _perform_on_delete(self, using: Optional[str] = None, keep_parents: bool = False) -> None:
        """
        Manually trigger relation field on_delete actions when soft deleting.

        Since we override the base model delete() method for soft deletion,
        on_delete actions are not automatically performed anymore.
        This method manually runs the ORM Collector to fetch all
        related instances and modify them according to their on_delete actions.

        Args:
            using: The database alias to use
            keep_parents: Whether to keep parent models when deleting
        """
        # Temporarily replace CASCADE actions with our custom SOFT_DELETE_CASCADE
        cascade_fields: List[ForeignObjectRel] = []
        for field in self._meta.get_fields():
            if isinstance(field, ForeignObjectRel) and field.on_delete == CASCADE:
                cascade_fields.append(field)
                field.on_delete = SOFT_DELETE_CASCADE

        # Ensure we revert CASCADE actions even if errors occur
        try:
            # Collect instances for updating and soft deleting
            using = using or router.db_for_write(self.__class__, instance=self)
            collector = Collector(using=using)
            collector.collect(objs=[self], keep_parents=keep_parents)

            with transaction.atomic(using=using, savepoint=False):
                # Handle only non-CASCADE field updates (like SET_NULL, SET_DEFAULT)
                for (field, value), instances_list in collector.field_updates.items():
                    # Skip processing if the field relates to a CASCADE relationship we're handling
                    if any(field == cascade_field for cascade_field in cascade_fields):
                        continue

                    updates = []
                    objs = []
                    for instances in instances_list:
                        if (
                                isinstance(instances, QuerySet)
                                and instances._result_cache is None
                        ):
                            updates.append(instances)
                        else:
                            objs.extend(instances)

                    # Handle QuerySet updates
                    if updates:
                        combined_updates = reduce(or_, updates)
                        combined_updates.update(**{field.name: value })

                    # Handle direct object updates
                    if objs:
                        model = objs[0].__class__
                        query = UpdateQuery(model)
                        query.update_batch(
                            pk_list=list({ obj.pk for obj in objs }),
                            values={field.name: value },
                            using=using
                        )

                # Delete all directly related instances
                for instance in getattr(collector, "soft_deletes", []):
                    if hasattr(instance, 'is_deleted'):
                        if not instance.is_deleted:
                            instance.delete()
                    elif hasattr(instance, 'deleted_at'):
                        if instance.deleted_at is None:
                            if hasattr(instance, 'delete'):
                                instance.delete()


        finally:
            # Restore original CASCADE actions
            for field in cascade_fields:
                field.on_delete = CASCADE