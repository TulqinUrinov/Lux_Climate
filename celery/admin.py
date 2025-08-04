from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.contrib import admin

admin.site.register(PeriodicTask)
admin.site.register(IntervalSchedule)
