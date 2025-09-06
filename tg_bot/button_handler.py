from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from tg_bot.message_handler import confirm_post_handler, preview_post


async def button_handler(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'start_post':
        context.user_data['post'] = {
            'photo': None,
            'video': None,
            'text': None,
            'step': None,
            'preview_message_id': None
        }

        buttons = [
            [InlineKeyboardButton("🎥 Video qo'shish", callback_data='add_video')],
            [InlineKeyboardButton("🖼️ Rasm qo'shish", callback_data='add_photo')],
            [InlineKeyboardButton("✏️ Matn qo'shish", callback_data='add_text')],
            [InlineKeyboardButton("❌ Bekor qilish", callback_data='cancel_post')],
        ]

        await query.message.reply_text(
            "Post yaratish boshlandi. Qo'shmoqchi bo'lgan qismni tanlang:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif query.data in ['add_video', 'add_photo', 'add_text', 'edit_text']:
        context.user_data['post']['step'] = query.data.replace('add_', '').replace('edit_', '')

        if query.data == 'add_video':
            msg = "🎥 Iltimos, video yuboring."
        elif query.data == 'add_photo':
            msg = "🖼️ Iltimos, rasm yuboring."
        elif query.data == 'add_text':
            msg = "✏️ Iltimos, matn yuboring."
        elif query.data == 'edit_text':
            msg = "✏️ Iltimos, yangi matn yuboring."

        await query.message.reply_text(msg)

    elif query.data == 'cancel_post':
        # Preview xabarni o'chirish
        post = context.user_data.get('post')
        if post and 'preview_message_id' in post:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=post['preview_message_id']
                )
            except:
                pass

        context.user_data['post'] = None
        await query.message.reply_text("❌ Post yuborish bekor qilindi.")

    elif query.data == 'confirm_post':
        await confirm_post_handler(update, context)

# async def button_handler(update, context):
#     query = update.callback_query
#     await query.answer()
#
#     if query.data == 'start_post':
#         context.user_data['post'] = {
#             'photo': None,
#             'video': None,
#             'text': None,
#             'step': None
#         }
#
#         buttons = [
#             [InlineKeyboardButton("🎥 Video qo‘shish", callback_data='add_video')],
#             [InlineKeyboardButton("🖼️ Rasm qo‘shish", callback_data='add_photo')],
#             [InlineKeyboardButton("✏️ Matn qo‘shish", callback_data='add_text')],
#             [InlineKeyboardButton("❌ Bekor qilish", callback_data='cancel_post')],
#         ]
#
#         await query.message.reply_text("Post yaratish boshlandi. Qo‘shmoqchi bo‘lgan qismni tanlang:",
#                                        reply_markup=InlineKeyboardMarkup(buttons))
#
#     elif query.data in ['add_video', 'add_photo', 'add_text']:
#         context.user_data['post']['step'] = query.data.replace('add_', '')
#
#         if query.data == 'add_video':
#             msg = "🎥 Iltimos, video yuboring."
#         elif query.data == 'add_photo':
#             msg = "🖼️ Iltimos, rasm yuboring."
#         elif query.data == 'add_text':
#             msg = "✏️ Iltimos, matn yuboring."
#
#         await query.message.reply_text(msg)
#
#     elif query.data == 'cancel_post':
#         context.user_data['post'] = None
#         await query.message.reply_text("❌ Post yuborish bekor qilindi.")
#
#
#     elif query.data == 'confirm_post':
#         await confirm_post_handler(update, context)
