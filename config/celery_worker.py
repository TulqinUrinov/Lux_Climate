import os
from celery import Celery
from datetime import timedelta

from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Aniq app nomlarini ko'rsatish
app.autodiscover_tasks(['data.payment'])

# Beat sozlamalari
app.conf.beat_schedule = {
    'check-installments-daily-10am': {
        'task': 'data.payment.tasks.check_upcoming_installments',
        'schedule': crontab(hour=10, minute=0),
    },
}

# app.conf.beat_schedule = {
#     'check-installments-daily': {
#         'task': 'data.payment.tasks.check_upcoming_installments',
#         'schedule': timedelta(minutes=1),
#     },
# }
