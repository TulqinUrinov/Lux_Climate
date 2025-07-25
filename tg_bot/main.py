import os
from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from data.bot.models import BotUser
from tg_bot.contact_handler import contact_handler


class Bot:

    async def start(self, update, context):
        user = update.effective_user
        bot_user = BotUser.objects.filter(chat_id=user.id).first()

        if not bot_user:
            text = "Pastdagi tugma orqali telefon raqamingizni yuboring 👇 "
            button = [
                [KeyboardButton("Share Contact", request_contact=True)]
            ]
            reply_markup = ReplyKeyboardMarkup(button, resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text(text=text, reply_markup=reply_markup)

        else:
            text = "Pastdagi tugmani bosing"
            button = [
                [
                    InlineKeyboardButton(text="Dasturga kirish",
                                         web_app=WebAppInfo(url="https://luxe-climate.vercel.app/"))
                ]
            ]
            reply_markup = InlineKeyboardMarkup(button)
            await update.message.reply_text(text=text,
                                            reply_markup=reply_markup,
                                            )

    def __init__(self):
        BOT_TOKEN = os.environ.get("BOT_TOKEN")
        self.app = ApplicationBuilder().token(BOT_TOKEN).build()
        self.app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
        self.app.add_handler(MessageHandler(filters.TEXT, self.start))

    def run(self):
        self.app.run_polling()
