from django.db import models
from typing import TYPE_CHECKING
from data.common.models import BaseModel

if TYPE_CHECKING:
    from data.customer.models import Customer
    from data.file.models import File


class Order(BaseModel):
    ORDER_CHOICES = (
        ('product', 'Product'),
        ('service', 'Service'),
    )

    GET_OR_GIVE = (
        ('get_order', 'Get_order'),
        ('give_order', 'Give_order')
    )

    customer: "Customer" = models.ForeignKey("customer.Customer", on_delete=models.SET_NULL, null=True, blank=True)
    order_type = models.CharField(choices=ORDER_CHOICES, max_length=10, default='order')
    get_or_give = models.CharField(choices=GET_OR_GIVE, max_length=20, default=' get_order')
    comment = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_installment = models.BooleanField(default=False)
    installment_count = models.PositiveIntegerField(null=True, blank=True)
    files: "File" = models.ManyToManyField("file.File", blank=True)
