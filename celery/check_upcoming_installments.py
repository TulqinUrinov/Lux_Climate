from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from send_reminder import send_payment_reminder
from data.payment.models import InstallmentPayment


@shared_task
def check_upcoming_installments():
    today = timezone.now().date()
    for days_left in [5, 3, 1]:
        target_date = today + timedelta(days=days_left)
        installments = InstallmentPayment.objects.filter(payment_date=target_date)

        for installment in installments:
            customer = installment.customer
            telegram_id = customer.bot_user.chat_id

            if customer and telegram_id:
                send_payment_reminder(
                    telegram_id=telegram_id,
                    days_left=days_left,
                    amount=installment.amount,
                    date=installment.payment_date
                )
            else:
                pass
