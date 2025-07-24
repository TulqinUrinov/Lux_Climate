import os

from telegram.ext import ApplicationBuilder, MessageHandler, filters


class Bot:

    async def start(self, update, context):
        user = update.effective_user

        await update.message.reply_text(text=f"Salom {user.full_name}")

    def __init__(self):
        BOT_TOKEN = os.environ.get("BOT_TOKEN")
        self.app = ApplicationBuilder().token(BOT_TOKEN).build()
        self.app.add_handler(MessageHandler(filters.TEXT, self.start))

    def run(self):
        self.app.run_polling()
