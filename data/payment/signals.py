from django.db.models.signals import post_save
from django.dispatch import receiver

from data.balance.models import Balance
from data.payment.models import Payment


@receiver(post_save, sender="payment.Payment")
def on_new_payment(sender, instance: Payment, created: bool, **kwargs):

    if not created:
        return

    Balance.objects.create(
        customer=instance.customer,
        user=instance.created_by,
        amount=instance.amount,
        reason=(
            "PAYMENT_INCOME" if instance.payment_type == "INCOME" else "PAYMENT_OUTCOME"
        ),
        comment=instance.comment,
        type="INCOME" if instance.payment_type == "INCOME" else "OUTCOME",
        change=instance.amount,
        payment=instance,
    )
