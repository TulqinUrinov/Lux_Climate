import os
from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo, ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters, CallbackQueryHandler
)

from data.bot.models import BotUser
from data.customer.models import Customer
from data.user.models import User
from tg_bot.button_handler import button_handler #, confirm_cancel_handler
from tg_bot.message_handler import message_handler


class Bot:

    def __init__(self):
        BOT_TOKEN = os.environ.get("BOT_TOKEN")
        self.app = ApplicationBuilder().token(BOT_TOKEN).build()
        self.app.add_handler(CallbackQueryHandler(button_handler,
                                                  pattern='^(start_post|add_video|add_photo|add_text|confirm_post|cancel_post)$'))
        # self.app.add_handler(CallbackQueryHandler(button_handler, pattern='^start_post$'))
        # self.app.add_handler(CallbackQueryHandler(confirm_cancel_handler, pattern='^(confirm_post|cancel_post)$'))
        self.app.add_handler(MessageHandler(filters.ALL, self.route_handler))

    def run(self):
        self.app.run_polling()

    async def route_handler(self, update, context):
        user_post = context.user_data.get("post")

        if user_post:
            await message_handler(update, context)
        elif update.message and update.message.text:
            await self.start(update, context)
        elif update.message.contact:
            await self.contact_handler(update, context)
        else:
            # boshqa holatlar uchun default javob
            await update.message.reply_text("Iltimos, to‘g‘ri buyruq yuboring.")

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
            reply_text = "Pastdagi tugmani bosing"
            reply_buttons = []

            if bot_user.user:
                url = "https://luxe-climate.vercel.app/"
                reply_buttons.append(
                    [
                        InlineKeyboardButton(
                            text="Dasturga kirish",
                            web_app=WebAppInfo(url=url),
                        )
                    ]
                )

                reply_buttons.append(
                    [
                        InlineKeyboardButton(
                            text="📝 Post yuborish",
                            callback_data="start_post",
                        )
                    ]
                )

            elif bot_user.customer:
                url = "https://luxe-climate.vercel.app/user_info"
                reply_buttons.append(
                    [
                        InlineKeyboardButton(
                            text="Dasturga kirish",
                            web_app=WebAppInfo(url=url),
                        )
                    ]
                )
            else:
                url = "https://luxe-climate.vercel.app/not-allowed"
                reply_buttons.append(
                    [
                        InlineKeyboardButton(
                            text="Dasturga kirish",
                            web_app=WebAppInfo(url=url),
                        )
                    ]
                )

            markup = InlineKeyboardMarkup(reply_buttons)
            await update.message.reply_text(text=reply_text, reply_markup=markup)

    async def contact_handler(self, update, context):
        contact = update.message.contact
        phone_number = contact.phone_number
        tg_user = update.effective_user

        print(phone_number)

        cleaned_phone = phone_number.lstrip('+')

        user_obj = User.objects.filter(phone_number=cleaned_phone).first()
        customer_obj = Customer.objects.filter(phone_number=cleaned_phone).first()

        msg = await update.message.reply_text(
            text="Ma'lumot tekshirilmoqda...",
            reply_markup=ReplyKeyboardRemove()
        )

        if user_obj:

            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg.message_id)

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

            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg.message_id)

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
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg.message_id)

            await update.message.reply_text(text="Telefon raqami topilmadi!!!")
