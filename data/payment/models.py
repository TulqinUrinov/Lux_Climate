from typing import TYPE_CHECKING

from django.db import models
from data.common.models import BaseModel

if TYPE_CHECKING:
    from data.user.models import User
    from data.customer.models import Customer
    from data.order.models import Order


class InstallmentPayment(BaseModel):
    order: "Order" = models.ForeignKey(
        "order.Order",
        models.CASCADE,
        related_name="order_splits",
    )

    customer = models.ForeignKey(
        "customer.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_splits",
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_date = models.DateField()

    left = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):

        if self.order is not None:
            self.customer = self.order.customer

        return self.save(*args, **kwargs)


class Payment(BaseModel):

    PAYMENT_TYPE_CHOICES = (
        ("CUSTOMER_TO_COMPANY", "Get Order"),
        ("COMPANY_TO_CUSTOMER", "Give Order"),
    )

    customer: "Customer | None" = models.ForeignKey(
        "customer.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )

    payment_type = models.CharField(max_length=255, choices=PAYMENT_TYPE_CHOICES)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    comment = models.TextField(null=True, blank=True)

    is_deleted = models.BooleanField(default=False)

    deleted_by: "User | None" = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_payments",
    )

    created_by: "User | None" = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_payments",
    )
