from django.db import models
from data.common.models import BaseModel
from data.order.models import Order
from data.customer.models import Customer


class Payment(BaseModel):
    customer: "Customer" = models.ForeignKey("customer.Customer", on_delete=models.CASCADE, related_name="payment")
    order: "Order" = models.ForeignKey("order.Order", models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    pay_date = models.DateField()

