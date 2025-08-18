import os
import requests
from django.dispatch import receiver

from data.bot.models import BotUser

PAYMENT_TYPE_LABELS = {
    "CUSTOMER_TO_COMPANY": "Chiqim",
    "COMPANY_TO_CUSTOMER": "Kirim",
}

PAYMENT_METHOD_LABELS = {
    "CLICK": "Click",
    "PAYME": "Payme",
    "CASH": "Naqd pul",
}


def send_payment_to_customer(payment):
    # Customer bilan bog‘langan BotUser topamiz
    if not payment.customer:
        return

    bot_user = payment.customer.bot_user.first()
    if not bot_user or not bot_user.chat_id:
        return  # Chat ID yo‘q bo‘lsa chiqib ketamiz


    customer_bot_users = []
    if payment.customer:
        customer_bot_users = list(payment.customer.bot_user.all())


    all_user_bot_users = list(
        BotUser.objects.filter(user__isnull=False)
    )


    bot_users = {bu.chat_id: bu for bu in (customer_bot_users + all_user_bot_users)}.values()

    if not bot_users:
        return

    # chat_id = bot_user.chat_id
    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    if payment.payment_type == "CUSTOMER_TO_COMPANY":
        sender = payment.customer.full_name
        receiver = payment.created_by.full_name if payment.created_by else "-"
    else:  # COMPANY_TO_CUSTOMER
        sender = payment.created_by.full_name if payment.created_by else "-"
        receiver = payment.customer.full_name

    # Turlarni tarjima qilish
    payment_type_label = PAYMENT_TYPE_LABELS.get(payment.payment_type, payment.payment_type)
    payment_method_label = PAYMENT_METHOD_LABELS.get(payment.payment_method, payment.payment_method)
    amount_str = f"{payment.amount:,.2f}".replace(",", " ")
    # Xabar matnini tayyorlash
    text = (
        f"💳 Yangi to‘lov\n"
        f"👤 To‘lov qiluvchi: {sender}\n"
        f"👤 To'lov qabul qiluvchi: {receiver}\n"
        f"💵 To‘lov usuli: {payment_method_label}\n"
        f"💰 Miqdor: {amount_str}\n"
        f"🧾 Izoh: {payment.comment or '-'}\n"

    )

    # Xabar yuborish
    # requests.post(
    #     f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    #     data={
    #         "chat_id": chat_id,
    #         "text": text
    #     }
    # )

    for bot_user in bot_users:
        if bot_user.chat_id:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={
                    "chat_id": bot_user.chat_id,
                    "text": text
                }
            )