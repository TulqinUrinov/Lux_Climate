from django.db.models.signals import post_save
from django.dispatch import receiver

from data.balance.models import Balance
from data.payment.models import Payment


@receiver(post_save, sender="payment.Payment")
def on_new_payment(sender, instance: Payment, created: bool, **kwargs):

    if not created:
        return

    instance.customer.recalculate_balance()
