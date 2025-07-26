from django.db import models

from data.common.models import BaseModel
from data.user.models import User
from data.customer.models import Customer
from data.order.models import Order


class Balance(BaseModel):
    REASON_CHOICES = (
        ('product', 'Product'),
        ('service', 'Service')
    )

    user: "User" = models.ForeignKey("user.User", on_delete=models.CASCADE)
    customer: "Customer" = models.ForeignKey("customer.Customer", on_delete=models.CASCADE)
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(choices=REASON_CHOICES, max_length=20)
    comment = models.TextField()
