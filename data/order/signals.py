from django.dispatch import receiver

from django.db.models.signals import post_save, post_delete

from data.order.models import Order


@receiver(post_save, sender=Order)
def on_order_create(sender, instance: Order, **kwargs):

    if instance.customer:
        instance.customer.recalculate_balance()


@receiver(post_delete, sender=Order)
def on_payment_delete(sender, instance: Order, **kwargs):
    if instance.customer:
        instance.customer.recalculate_balance()
