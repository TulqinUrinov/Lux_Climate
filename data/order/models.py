from django.db import models
from typing import TYPE_CHECKING
from data.common.models import BaseModel


if TYPE_CHECKING:
    from data.customer.models import Customer
    from data.file.models import File
    from data.payment.models import InstallmentPayment
    from data.user.models import User


class Order(BaseModel):
    PRODUCT_CHOICES = (
        ("PRODUCT", "Product"),
        ("SERVICE", "Service"),
    )

    ORDER_TYPE_CHOICES = (
        ("CUSTOMER_TO_COMPANY", "Get Order"),
        ("COMPANY_TO_CUSTOMER", "Give Order"),
    )

    customer: "Customer" = models.ForeignKey(
        "customer.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    product = models.CharField(
        choices=PRODUCT_CHOICES,
        max_length=10,
    )

    order_type = models.CharField(
        choices=ORDER_TYPE_CHOICES,
        max_length=20,
    )

    comment = models.TextField(blank=True, null=True)

    # so'mdagi narxi
    price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
    )

    # dollar kursi
    usd_course = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # dollar miqdori
    usd_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    is_installment = models.BooleanField(default=False)

    installment_count = models.PositiveIntegerField(default=0)

    created_by: "User" = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_orders",
    )

    files: "File" = models.ManyToManyField("file.File", blank=True)

    order_splits: "models.QuerySet[InstallmentPayment]"
