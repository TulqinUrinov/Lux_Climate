from django.db import models
from rest_framework.exceptions import ValidationError

from data.common.models import BaseModel


class User(BaseModel):
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True)
    tg_chat_id = models.BigIntegerField(null=True, blank=True, unique=True)
    is_archived = models.BooleanField(default=False)

    def clean(self):
        super().clean()

        cleaned_phone = self.phone_number.lstrip('+') if self.phone_number else None

        from data.customer.models import Customer

        if cleaned_phone and Customer.objects.filter(phone_number=cleaned_phone).exists():
            raise ValidationError("Bu telefon raqami allaqachon Customer sifatida mavjud.")

        # Modelga + belgisisiz telefon raqamni yozamiz
        self.phone_number = cleaned_phone

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name
