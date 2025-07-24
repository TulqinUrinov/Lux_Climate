from django.contrib import admin

from data.bot.models import BotUser


@admin.register(BotUser)
class AdminBotUser(admin.ModelAdmin):
    list_display = ('tg_name','username', 'chat_id')
