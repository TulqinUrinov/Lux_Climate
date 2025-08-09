import os
import requests

PAYMENT_TYPE_LABELS = {
    "CUSTOMER_TO_COMPANY": "To‘lov qabul qilish",
    "COMPANY_TO_CUSTOMER": "To‘lov berish",
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

    chat_id = bot_user.chat_id
    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    # Turlarni tarjima qilish
    payment_type_label = PAYMENT_TYPE_LABELS.get(payment.payment_type, payment.payment_type)
    payment_method_label = PAYMENT_METHOD_LABELS.get(payment.payment_method, payment.payment_method)
    amount_str = f"{payment.amount:,.2f}".replace(",", " ")
    # Xabar matnini tayyorlash
    text = (
        f"💳 Yangi to‘lov\n"
        f"📌 To‘lov turi: {payment_type_label}\n"
        f"💵 To‘lov usuli: {payment_method_label}\n"
        f"💰 Miqdor: {amount_str}\n"
        f"👤 Qabul qilgan: {payment.created_by.full_name if payment.created_by else '-'}\n"
        f"🧾 Izoh: {payment.comment or '-'}\n"

    )

    # Xabar yuborish
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": text
        }
    )