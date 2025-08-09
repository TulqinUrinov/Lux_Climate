import json
import os

import requests


def send_order_to_customer(order):
    # Customer bilan bog‘langan BotUser topamiz
    bot_user = order.customer.bot_user.first()
    if not bot_user or not bot_user.chat_id:
        return  # Chat ID yo‘q bo‘lsa, hech narsa qilmaymiz

    chat_id = bot_user.chat_id

    PRODUCT_LABELS = {
        "PRODUCT": "Mahsulot",
        "SERVICE": "Xizmat",
    }

    ORDER_TYPE_LABELS = {
        "CUSTOMER_TO_COMPANY": "Buyurtma qabul qilish",
        "COMPANY_TO_CUSTOMER": "Buyurtma berish",
    }

    product_label = PRODUCT_LABELS.get(order.product, order.product)
    order_type_label = ORDER_TYPE_LABELS.get(order.order_type, order.order_type)

    text = (
        f"🆕 Yangi buyurtma\n"
        f"📌 Mahsulot turi: {product_label}\n"
        f"📦 Buyurtma turi: {order_type_label}\n"
        f"💰 Narx: {order.price}\n"
        f"📄 Izoh: {order.comment or '-'}\n"
    )

    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    # Agar PRODUCT bo'lsa va fayllar bo'lsa — sendMediaGroup ishlatamiz
    if order.product == "PRODUCT" and order.files.exists():
        files = {}
        media = []

        for idx, file in enumerate(order.files.all()):
            if file.file:
                file_key = f"file{idx}"
                files[file_key] = open(file.file.path, "rb")
                media_item = {
                    "type": "document",
                    "media": f"attach://{file_key}"
                }
                # Faqat birinchi faylga caption qo'yamiz
                if idx == 0:
                    media_item["caption"] = text
                media.append(media_item)

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup",
            data={"chat_id": chat_id, "media": json.dumps(media)},
            files=files
        )

    else:
        # Fayl bo'lmasa — faqat matn yuboramiz
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": chat_id, "text": text}
        )
