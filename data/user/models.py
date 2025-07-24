from django.db import models
from data.common.models import BaseModel


class User(BaseModel):
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.full_name
