import json
import os

import requests

from data.bot.models import BotUser


def send_order_to_customer(order):
    # # Customer bilan bog‘langan BotUser topamiz
    # bot_user = order.customer.bot_user.first()
    # if not bot_user or not bot_user.chat_id:
    #     return  # Chat ID yo‘q bo‘lsa, hech narsa qilmaymiz
    #
    # chat_id = bot_user.chat_id

    if not order.customer:
        return

    customer_bot_users = []
    if order.customer:
        customer_bot_users = list(order.customer.bot_user.all())

    all_user_bot_users = list(
        BotUser.objects.filter(user__isnull=False)  # admin yoki user bog‘langanlar
    )

    # Unikal chat_id larni olish
    bot_users = {bu.chat_id: bu for bu in (customer_bot_users + all_user_bot_users)}.values()

    if not bot_users:
        return

    PRODUCT_LABELS = {
        "PRODUCT": "Mahsulot",
        "SERVICE": "Xizmat",
    }

    ORDER_TYPE_LABELS = {
        "CUSTOMER_TO_COMPANY": "Buyurtma qabul qilish",
        "COMPANY_TO_CUSTOMER": "Buyurtma berish",
    }

    if order.order_type == "CUSTOMER_TO_COMPANY":
        sender = order.customer.full_name
        receiver = order.created_by.full_name if order.created_by else "-"
    else:  # COMPANY_TO_CUSTOMER
        sender = order.created_by.full_name if order.created_by else "-"
        receiver = order.customer.full_name

    product_label = PRODUCT_LABELS.get(order.product, order.product)
    order_type_label = ORDER_TYPE_LABELS.get(order.order_type, order.order_type)
    price_str = f"{order.price:,.2f}".replace(",", " ")
    text = (
        f"🆕 Yangi buyurtma\n"
        f"👤 Buyurtma beruvchi: {sender}\n"
        f"👤 Buyurtma qabul qiluvchi: {receiver}\n"
        f"📌 Mahsulot turi: {product_label}\n"
        f"📦 Buyurtma turi: {order_type_label}\n"
        f"💰 Narx: {price_str}\n"
        f"📄 Izoh: {order.comment or '-'}\n"
    )

    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    for bot_user in bot_users:
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
                    if idx == 0:
                        media_item["caption"] = text
                    media.append(media_item)

            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup",
                data={"chat_id": bot_user.chat_id, "media": json.dumps(media)},
                files=files
            )
        else:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={"chat_id": bot_user.chat_id, "text": text}
            )

    # # Agar PRODUCT bo'lsa va fayllar bo'lsa — sendMediaGroup ishlatamiz
    # if order.product == "PRODUCT" and order.files.exists():
    #     files = {}
    #     media = []
    #
    #     for idx, file in enumerate(order.files.all()):
    #         if file.file:
    #             file_key = f"file{idx}"
    #             files[file_key] = open(file.file.path, "rb")
    #             media_item = {
    #                 "type": "document",
    #                 "media": f"attach://{file_key}"
    #             }
    #             # Faqat birinchi faylga caption qo'yamiz
    #             if idx == 0:
    #                 media_item["caption"] = text
    #             media.append(media_item)
    #
    #     requests.post(
    #         f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup",
    #         data={"chat_id": chat_id, "media": json.dumps(media)},
    #         files=files
    #     )
    #
    # else:
    #     # Fayl bo'lmasa — faqat matn yuboramiz
    #     requests.post(
    #         f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    #         data={"chat_id": chat_id, "text": text}
    #     )
