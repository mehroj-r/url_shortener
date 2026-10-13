from typing import Optional

from django.db import models, router, transaction
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from core.managers import SoftDeleteManager, restore_queryset, soft_delete_queryset


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        abstract = True


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
        Soft delete the object, and every live object that CASCADEs from it,
        by setting their deleted_at timestamp.
        """
        using = using or router.db_for_write(self.__class__, instance=self)
        deleted_at = timezone.now()

        with transaction.atomic(using=using):
            soft_delete_queryset(self.__class__._base_manager.using(using).filter(pk=self.pk), deleted_at)

        self.deleted_at = deleted_at

    def hard_delete(self, using: Optional[str] = None, keep_parents: bool = False) -> None:
        """
        Permanently delete the object from the database.
        """
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self) -> None:
        """
        Restore a soft-deleted object, together with the objects that were
        soft deleted along with it.
        """
        if self.deleted_at is None:
            return

        using = router.db_for_write(self.__class__, instance=self)
        with transaction.atomic(using=using):
            restore_queryset(self.__class__._base_manager.using(using).filter(pk=self.pk), self.deleted_at)

        self.deleted_at = None

    class Meta:
        abstract = True
