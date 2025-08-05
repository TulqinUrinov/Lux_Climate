import os
from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from data.bot.models import BotUser
# from tg_bot.contact_handler import contact_handler

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from data.bot.models import BotUser
from data.customer.models import Customer
from data.user.models import User


class Bot:

    async def start(self, update, context):
        user = update.effective_user
        bot_user = BotUser.objects.filter(chat_id=user.id).first()

        if not bot_user:
            text = "Pastdagi tugma orqali telefon raqamingizni yuboring 👇 "
            button = [[KeyboardButton("Share Contact", request_contact=True)]]
            reply_markup = ReplyKeyboardMarkup(
                button, resize_keyboard=True, one_time_keyboard=True
            )
            await update.message.reply_text(text=text, reply_markup=reply_markup)

        else:
            if bot_user.user:
                url = "https://luxe-climate.vercel.app/"
            elif bot_user.customer:
                url = "https://luxe-climate.vercel.app/user_info"
            else:
                url = "https://luxe-climate.vercel.app/not-allowed"

            text = "Pastdagi tugmani bosing"
            button = [
                [
                    InlineKeyboardButton(
                        text="Dasturga kirish",
                        web_app=WebAppInfo(url=url),
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(button)

            await update.message.reply_text(
                text=text,
                reply_markup=reply_markup,
            )

    def __init__(self):
        BOT_TOKEN = os.environ.get("BOT_TOKEN")
        self.app = ApplicationBuilder().token(BOT_TOKEN).build()
        self.app.add_handler(MessageHandler(filters.CONTACT, self.contact_handler))
        self.app.add_handler(MessageHandler(filters.TEXT, self.start))

    def run(self):
        self.app.run_polling()

    async def contact_handler(self, update, context):
        contact = update.message.contact
        phone_number = contact.phone_number
        tg_user = update.effective_user

        print(phone_number)

        user_obj = User.objects.filter(phone_number=phone_number).first()
        customer_obj = Customer.objects.filter(phone_number=phone_number).first()

        if user_obj:
            bot_user, _ = BotUser.objects.get_or_create(
                chat_id=tg_user.id,
                defaults={
                    "tg_name": tg_user.full_name,
                    "username": tg_user.username,
                    "user": user_obj,
                },
            )

            return await self.start(update, context)

        elif customer_obj:
            bot_user, _ = BotUser.objects.get_or_create(
                chat_id=tg_user.id,
                defaults={
                    "tg_name": tg_user.full_name,
                    "username": tg_user.username,
                    "customer": customer_obj,
                },
            )

            return await self.start(update, context)

        else:
            await update.message.reply_text(text="Telefon raqami topilmadi!!!")
