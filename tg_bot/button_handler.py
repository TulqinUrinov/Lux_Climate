async def button_handler(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'start_post':
        context.user_data['post'] = {
            'photo': None,
            'video': None,
            'text': None
        }
        await query.message.reply_text("Post yuborish rejimi: Iltimos, rasm/video va text yuboring.")


async def confirm_cancel_handler(update, context):
    query = update.callback_query
    data = query.data
    post = context.user_data.get('post')

    await query.answer()

    if data == 'cancel_post':
        context.user_data['post'] = None
        await query.message.reply_text("❌ Post yuborish bekor qilindi.")
        return

    elif data == 'confirm_post':
        # Foydalanuvchilarga yuborish
        from data.bot.models import BotUser
        customers = BotUser.objects.filter(customer__isnull=False)

        count = 0
        for user in customers:
            chat_id = user.chat_id
            try:
                if post['video']:
                    await context.bot.send_video(chat_id, video=post['video'], caption=post['text'])
                elif post['photo']:
                    await context.bot.send_photo(chat_id, photo=post['photo'], caption=post['text'])
                elif post['text']:
                    await context.bot.send_message(chat_id, text=post['text'])
                count += 1
            except Exception as e:
                print(f"Xato: {e} - {chat_id}")

        context.user_data['post'] = None
        await query.message.reply_text(f"✅ Post muvaffaqiyatli {count} ta foydalanuvchiga yuborildi.")
