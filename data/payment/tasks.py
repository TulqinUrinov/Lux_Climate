from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from data.payment.send_reminder import send_payment_reminder
from data.payment.models import InstallmentPayment


@shared_task(bind=True, name='data.payment.tasks.check_upcoming_installments')
def check_upcoming_installments(self):
    today = timezone.now().date()
    for days_left in [5, 3, 1]:
        target_date = today + timedelta(days=days_left)
        installments = InstallmentPayment.objects.filter(payment_date=target_date)

        for installment in installments:
            customer = installment.customer
            telegram_id = getattr(getattr(customer, 'bot_user', None), 'chat_id', None)

            if telegram_id:
                print(f"Processing reminder for Telegram ID: {telegram_id}")
                send_payment_reminder(
                    telegram_id=telegram_id,
                    days_left=days_left,
                    amount=installment.amount,
                    date=installment.payment_date
                )
            else:
                print(f"No Telegram ID found for customer {getattr(customer, 'id', 'unknown')}")