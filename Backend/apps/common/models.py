from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base: every domain model inherits this."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ActiveManager(models.Manager):
    """Default manager - filters to is_active=True only."""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class SoftDeleteModel(TimeStampedModel):
    """
    Abstract base adding is_active. .delete() is overridden to set
    is_active=False and save - never actually removing the row (medical
    records must never be hard-deleted). .hard_delete() exists for genuine
    removal but is never called from normal app flow.
    """

    is_active = models.BooleanField(default=True)

    objects = ActiveManager()  # default: filtered to is_active=True
    all_objects = models.Manager()  # unfiltered: Django admin, admin-oversight views

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
