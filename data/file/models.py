from django.db import models
from data.common.models import BaseModel


class File(BaseModel):
    file = models.FileField(upload_to='files')
