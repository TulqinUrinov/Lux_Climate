from django.db import models
from data.common.models import BaseModel
from data.order.models import Order


class InstallmentPayment(BaseModel):
    order: "Order" = models.ForeignKey("order.Order", models.CASCADE, related_name='installmentpayment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
