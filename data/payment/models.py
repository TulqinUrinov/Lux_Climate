from typing import TYPE_CHECKING

from django.db import models
from data.common.models import BaseModel

if TYPE_CHECKING:
    from data.user.models import User
    from data.customer.models import Customer
    from data.order.models import Order


class InstallmentPayment(BaseModel):
    ORDER_TYPE_CHOICES = (
        ("CUSTOMER_TO_COMPANY", "Get Order"),
        ("COMPANY_TO_CUSTOMER", "Give Order"),
    )

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

    order_type = models.CharField(
        max_length=255,
        choices=ORDER_TYPE_CHOICES,
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_date = models.DateField()

    left = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.order is not None:
            self.customer = self.order.customer
            self.order_type = self.order.order_type

        return super().save(*args, **kwargs)


class Payment(BaseModel):
    PAYMENT_TYPE_CHOICES = (
        ("CUSTOMER_TO_COMPANY", "Get Order"),
        ("COMPANY_TO_CUSTOMER", "Give Order"),
    )

    PAYMENT_METHOD_CHOICES = (
        ("CLICK", "Click"),
        ("PAYME", "Payme"),
        ("CASH", "Naqd Pul"),
    )

    customer: "Customer | None" = models.ForeignKey(
        "customer.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )

    payment_type = models.CharField(max_length=255, choices=PAYMENT_TYPE_CHOICES)

    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)

    amount = models.DecimalField(max_digits=20, decimal_places=2)

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
