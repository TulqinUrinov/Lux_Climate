from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from data.bot.models import BotUser
from data.customer.models import Customer
from data.user.models import User


async def contact_handler(update, context):
    contact = update.message.contact
    phone_number = contact.phone_number
    tg_user = update.effective_user

    user_obj = User.objects.filter(phone_number=phone_number).first()
    customer_obj = Customer.objects.filter(phone_number=phone_number).first()

    if user_obj:
        bot_user, _ = BotUser.objects.get_or_create(
            chat_id=tg_user.id,
            defaults={
                'tg_name': tg_user.full_name,
                'username': tg_user.username,
                'user': user_obj
            }
        )
        text = "Pastdagi tugmani bosing"
        button = [
            [
                InlineKeyboardButton(text="Dasturga kirish",
                                     url="https://luxe-climate.vercel.app/")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(button)

        await update.message.reply_text(text=text, reply_markup=reply_markup)


    elif customer_obj:
        bot_user, _ = BotUser.objects.get_or_create(
            chat_id=tg_user.id,
            defaults={
                'tg_name': tg_user.full_name,
                'username': tg_user.username,
                'customer': customer_obj
            }
        )
        text = "Pastdagi tugmani bosing"
        button = [
            [
                InlineKeyboardButton(text="Dasturga kirish",
                                     url="https://luxe-climate.vercel.app/user_info")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(button)

        await update.message.reply_text(text=text, reply_markup=reply_markup)


    else:
        await update.message.reply_text(text="Telefon raqami topilmadi!!!")
