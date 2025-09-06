from telegram import InlineKeyboardButton, InlineKeyboardMarkup


async def preview_post(update, context):
    post = context.user_data.get('post')
    if not post:
        return

    buttons = []
    if not post.get('video'):
        buttons.append([InlineKeyboardButton("🎥 Video qo‘shish", callback_data='add_video')])
    if not post.get('photo'):
        buttons.append([InlineKeyboardButton("🖼️ Rasm qo‘shish", callback_data='add_photo')])

    if not post.get('text'):
        buttons.append([InlineKeyboardButton("✏️ Matn qo‘shish", callback_data='add_text')])
    else:
        buttons.append([InlineKeyboardButton("✏️ Matnni tahrirlash", callback_data='edit_text')])

    buttons += [
        [InlineKeyboardButton("✅ Tasdiqlash", callback_data='confirm_post')],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data='cancel_post')],
    ]
    markup = InlineKeyboardMarkup(buttons)

    # oldingi preview message saqlangan bo'lsa uni tahrir qilamiz
    preview_msg = context.user_data.get("preview_msg")

    try:
        if preview_msg:
            if post.get('video') or post.get('photo'):
                await preview_msg.edit_caption(caption=post.get('text', ''), reply_markup=markup)
            elif post.get('text'):
                await preview_msg.edit_text(text=post.get('text'), reply_markup=markup)
            else:
                await preview_msg.edit_text("Postga hech narsa qo‘shilmadi. Iltimos, media yoki matn yuboring.",
                                            reply_markup=markup)
            return
    except Exception as e:
        print("Preview update xatolik:", e)

    # agar preview message yo‘q bo‘lsa, yangi yuboramiz va saqlaymiz
    if post.get('video'):
        preview_msg = await update.message.reply_video(video=post['video'], caption=post.get('text', ''), reply_markup=markup)
    elif post.get('photo'):
        preview_msg = await update.message.reply_photo(photo=post['photo'], caption=post.get('text', ''), reply_markup=markup)
    elif post.get('text'):
        preview_msg = await update.message.reply_text(post['text'], reply_markup=markup)
    else:
        preview_msg = await update.message.reply_text("Postga hech narsa qo‘shilmadi. Iltimos, media yoki matn yuboring.",
                                                      reply_markup=markup)

    context.user_data["preview_msg"] = preview_msg


# async def preview_post(update, context):
#     post = context.user_data.get('post')
#
#     buttons = []
#
#     if not post['video']:
#         buttons.append([InlineKeyboardButton("🎥 Video qo‘shish", callback_data='add_video')])
#     if not post['photo']:
#         buttons.append([InlineKeyboardButton("🖼️ Rasm qo‘shish", callback_data='add_photo')])
#     if not post['text']:
#         buttons.append([InlineKeyboardButton("✏️ Matn qo‘shish", callback_data='add_text')])
#
#     buttons += [
#         [InlineKeyboardButton("✅ Tasdiqlash", callback_data='confirm_post')],
#         [InlineKeyboardButton("❌ Bekor qilish", callback_data='cancel_post')],
#     ]
#
#     markup = InlineKeyboardMarkup(buttons)
#
#     if post['video']:
#         await update.message.reply_video(video=post['video'], caption=post.get('text', ''), reply_markup=markup)
#     elif post['photo']:
#         await update.message.reply_photo(photo=post['photo'], caption=post.get('text', ''), reply_markup=markup)
#     elif post['text']:
#         await update.message.reply_text(post['text'], reply_markup=markup)
#     else:
#         await update.message.reply_text("Postga hech narsa qo‘shilmadi. Iltimos, media yoki matn yuboring.",
#                                         reply_markup=markup)


async def message_handler(update, context):
    post = context.user_data.get('post')
    if not post or not post.get('step'):
        return

    step = post['step']
    msg = update.message

    if step == 'video' and msg.video:
        post['video'] = msg.video.file_id
    elif step == 'photo' and msg.photo:
        post['photo'] = msg.photo[-1].file_id
    elif step == 'text' and msg.text:
        post['text'] = msg.text
    else:
        await msg.reply_text("❗ Noto‘g‘ri format. Iltimos, to‘g‘ri fayl yuboring.")
        return

    post['step'] = None
    context.user_data['post'] = post

    await preview_post(update, context)


async def confirm_post_handler(update, context):
    query = update.callback_query
    await query.answer()

    post = context.user_data.get('post')
    from data.bot.models import BotUser

    customers = BotUser.objects.filter(customer__isnull=False)
    count = 0

    for user in customers:
        try:
            if post['video']:
                await context.bot.send_video(chat_id=user.chat_id, video=post['video'], caption=post.get('text', ''))
            elif post['photo']:
                await context.bot.send_photo(chat_id=user.chat_id, photo=post['photo'], caption=post.get('text', ''))
            elif post['text']:
                await context.bot.send_message(chat_id=user.chat_id, text=post['text'])
            count += 1
        except Exception as e:
            print(f"Xato: {e} - {user.chat_id}")

    context.user_data['post'] = None
    await query.message.reply_text(f"✅ Post {count} ta mijozga yuborildi.")
