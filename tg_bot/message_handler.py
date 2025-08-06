from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def message_handler(update, context):
    # Agar post hali boshlangan bo'lmasa, e'tibor bermaymiz
    user_post = context.user_data.get('post')
    if not user_post:
        return

    # Kontekstni yangilaymiz
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        user_post['photo'] = file_id

    elif update.message.video:
        file_id = update.message.video.file_id
        user_post['video'] = file_id

    elif update.message.text:
        user_post['text'] = update.message.text

    context.user_data['post'] = user_post

    # Inline tugmalar
    buttons = [
        [InlineKeyboardButton("✅ Tasdiqlash", callback_data='confirm_post')],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data='cancel_post')],
    ]
    markup = InlineKeyboardMarkup(buttons)

    # Eski preview xabarini o‘chirmay yangi preview yuboriladi
    if user_post.get('photo'):
        await update.message.reply_photo(photo=user_post['photo'])

    if user_post.get('video'):
        await update.message.reply_video(video=user_post['video'])

    if user_post.get('text'):
        await update.message.reply_text(user_post['text'])

    # Yakuniy: tasdiqlash/bekor qilish tugmalari
    await update.message.reply_text("Postni tasdiqlaysizmi?", reply_markup=markup)

# async def message_handler(update, context):
#     user_post = context.user_data.get('post')
#
#     if not user_post:
#         return  # Foydalanuvchi post rejimida emas
#
#     if update.message.photo:
#         file_id = update.message.photo[-1].file_id
#         user_post['photo'] = file_id
#
#     elif update.message.video:
#         file_id = update.message.video.file_id
#         user_post['video'] = file_id
#
#     elif update.message.text:
#         user_post['text'] = update.message.text
#
#     context.user_data['post'] = user_post
#
#     # Preview tayyorlash
#     buttons = [
#         [InlineKeyboardButton("✅ Tasdiqlash", callback_data='confirm_post')],
#         [InlineKeyboardButton("❌ Bekor qilish", callback_data='cancel_post')],
#     ]
#     markup = InlineKeyboardMarkup(buttons)
#
#     if user_post['video']:
#         await update.message.reply_video(video=user_post['video'], caption=user_post['text'], reply_markup=markup)
#     elif user_post['photo']:
#         await update.message.reply_photo(photo=user_post['photo'], caption=user_post['text'], reply_markup=markup)
#     elif user_post['text']:
#         await update.message.reply_text(user_post['text'], reply_markup=markup)
