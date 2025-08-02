from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from data.payment.models import Payment


@receiver(post_save, sender="payment.Payment")
def on_new_payment(sender, instance: Payment, created: bool, **kwargs):

    if instance.customer:
        instance.customer.recalculate_balance()


@receiver(post_delete, sender=Payment)
def on_payment_delete(sender, instance: Payment, **kwargs):
    if instance.customer:
        instance.customer.recalculate_balance()
