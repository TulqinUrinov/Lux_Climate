from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from data.payment.send_reminder import send_payment_reminder
from data.payment.models import InstallmentPayment

from data.bot.models import BotUser


@shared_task(bind=True, name='data.payment.tasks.check_upcoming_installments')
def check_upcoming_installments(self):
    today = timezone.now().date()
    for days_left in [5, 3, 1]:
        target_date = today + timedelta(days=days_left)
        installments = InstallmentPayment.objects.filter(payment_date=target_date)

        for installment in installments:
            customer = installment.customer
            payment_date = installment.payment_date.strftime("%d-%m-%Y")

            print(customer)

            bot_user = BotUser.objects.filter(customer=customer).first()
            telegram_id = bot_user.chat_id

            if telegram_id:
                print(f"Processing reminder for Telegram ID: {telegram_id}")
                send_payment_reminder(
                    telegram_id=telegram_id,
                    # telegram_id=5575104582,
                    days_left=days_left,
                    amount=installment.amount,
                    date=payment_date,
                )
            else:
                print(f"No Telegram ID found for customer {getattr(customer, 'id', 'unknown')}")
