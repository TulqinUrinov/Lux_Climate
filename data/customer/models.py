from data.common.models import BaseModel
from django.db import models


class Customer(BaseModel):
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True)
    get_order = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name
