from typing import TYPE_CHECKING
from django.db import models

from data.common.models import BaseModel

if TYPE_CHECKING:
    from data.user.models import User
    from data.payment.models import Payment
    from data.customer.models import Customer


class Balance(BaseModel):
    REASON_CHOICES = (
        ("ORDER", "Order"),
        ("PAYMENT_INCOME", "Payment Income"),
        ("PAYMENT_OUTCOME", "Payment Outcome"),
    )

    TRANSACTION_CHOICES = (
        ("INCOME", "Income"),
        ("OUTCOME", "Outcome"),
    )

    user: "User" = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    customer: "Customer" = models.ForeignKey(
        "customer.Customer",
        on_delete=models.CASCADE,
        related_name="balances",
    )

    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
    )

    reason = models.CharField(
        choices=REASON_CHOICES,
        max_length=20,
        default="payment",
    )

    comment = models.TextField(null=True, blank=True)

    type = models.CharField(
        choices=TRANSACTION_CHOICES,
        max_length=20,
        default="income",
    )

    change = models.DecimalField(
        max_digits=20,
        decimal_places=2,
    )

    payment: "Payment" = models.OneToOneField(
        "payment.Payment",
        on_delete=models.SET_NULL,
        related_name="_balance",
        null=True,
        blank=True,
    )

    payment_choice = models.CharField(
        max_length=20,
        choices=payment.PAYMENT_CHOICES,
        null=True,
        blank=True
    )
