from django.db import models
from data.common.models import BaseModel


class User(BaseModel):
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True)

    def clean(self):
        super().clean()
        if self.phone_number and self.phone_number.startswith('+'):
            self.phone_number = self.phone_number[1:]  # + ni olib tashlaymiz

    def save(self, *args, **kwargs):
        self.full_clean()  # clean() metodini avtomatik chaqiramiz
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name
