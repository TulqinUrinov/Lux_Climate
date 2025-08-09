import os

from django.conf import settings
import requests


def send_order_to_customer(order):
    # Customer bilan bog‘langan BotUser topamiz
    bot_user = order.customer.bot_user.first()
    if not bot_user or not bot_user.chat_id:
        return  # Chat ID yo‘q bo‘lsa, hech narsa qilmaymiz

    chat_id = bot_user.chat_id

    # Xabar matnini tayyorlash
    text = (
        f"🆕 Yangi buyurtma\n"
        f"📌 Mahsulot turi: {order.get_product_display()}\n"
        f"📦 Buyurtma turi: {order.get_order_type_display()}\n"
        f"💰 Narx: {order.price}\n"
        f"📄 Izoh: {order.comment or '-'}\n"
    )

    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    # Xabar yuborish
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={
        "chat_id": chat_id,
        "text": text
    })

    if order.product == "PRODUCT" and order.files.exists():
        for file in order.files.all():
            if file.file:  # Fayl mavjud bo‘lsa
                with open(file.file.path, "rb") as f:
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                        data={"chat_id": chat_id},
                        files={"document": f}
                    )
