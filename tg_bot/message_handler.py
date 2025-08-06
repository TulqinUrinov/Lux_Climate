from telegram import InlineKeyboardButton, InlineKeyboardMarkup


async def message_handler(update, context):
    user_post = context.user_data.get('post')

    if not user_post:
        return  # Foydalanuvchi post rejimida emas

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        user_post['photo'] = file_id

    elif update.message.video:
        file_id = update.message.video.file_id
        user_post['video'] = file_id

    elif update.message.text:
        user_post['text'] = update.message.text

    context.user_data['post'] = user_post

    # Preview tayyorlash
    buttons = [
        [InlineKeyboardButton("✅ Tasdiqlash", callback_data='confirm_post')],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data='cancel_post')],
    ]
    markup = InlineKeyboardMarkup(buttons)

    if user_post['video']:
        await update.message.reply_video(video=user_post['video'], caption=user_post['text'], reply_markup=markup)
    elif user_post['photo']:
        await update.message.reply_photo(photo=user_post['photo'], caption=user_post['text'], reply_markup=markup)
    elif user_post['text']:
        await update.message.reply_text(user_post['text'], reply_markup=markup)
