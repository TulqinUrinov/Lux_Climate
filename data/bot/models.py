from data.common.models import BaseModel
from django.db import models

from data.customer.models import Customer
from data.user.models import User


class BotUser(BaseModel):
    chat_id = models.BigIntegerField(unique=True)

    tg_name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)

    user: "User" = models.ForeignKey("user.User",
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     blank=True)

    customer: "Customer" = models.ForeignKey("customer.Customer",
                                             on_delete=models.SET_NULL,
                                             null=True,
                                             blank=True)

    def __str__(self):
        return self.tg_name
