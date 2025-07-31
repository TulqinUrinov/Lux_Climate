from django.db import models

from data.common.models import BaseModel
from data.user.models import User
from data.customer.models import Customer
from data.order.models import Order


class Balance(BaseModel):
    REASON_CHOICES = (
        ('order', 'Order'),
        ('payment', 'Payment')
    )

    TRANSACTION_CHOICES = (
        ("income", "Income"),
        ("outcome", "Outcome")
    )

    user: "User" = models.ForeignKey("user.User", on_delete=models.CASCADE)
    customer: "Customer" = models.ForeignKey("customer.Customer", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(choices=REASON_CHOICES, max_length=20, default='payment')
    comment = models.TextField()
    type = models.CharField(choices=TRANSACTION_CHOICES, max_length=20, default='income')
    change = models.DecimalField(max_digits=10, decimal_places=2)
