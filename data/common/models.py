from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ActiveCustomerManager(models.Manager):
    """Faol (is_archived=False) mijozlarga tegishli obyektlarni chiqaradi."""

    def get_queryset(self):
        return super().get_queryset().filter(customer__is_archived=False)
