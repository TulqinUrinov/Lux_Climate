import os
from datetime import timedelta

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.conf.beat_schedule = {
    'check-installments-daily': {
        'task': 'data.payment.tasks.check_upcoming_installments',
        'schedule': timedelta(days=1),  # har kuni
    },
}
