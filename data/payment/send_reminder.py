import os

import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN")


def send_payment_reminder(telegram_id, days_left, amount, date):
    text = (
        f"📢 To'lov kuniga ({date})  {days_left} kun qoldi!\n"
        f"💸 To‘lov summasi: {amount} so‘m."
    )
    token = BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": telegram_id,
        "text": text,
    }
    requests.post(url, data=data)
