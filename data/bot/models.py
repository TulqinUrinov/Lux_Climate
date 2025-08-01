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

    @property
    def is_authenticated(self):
        return True

    @property
    def full_name(self):
        if self.customer:
            return self.customer.full_name
        if self.user:
            return self.user.full_name
        return self.tg_name or self.username

    @property
    def phone_number(self):
        if self.customer:
            return self.customer.phone_number
        if self.user:
            return self.user.phone_number
        return None

    def __str__(self):
        return self.tg_name
