from django.contrib import admin
from data.customer.models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'tg_chat_id', 'is_archived', 'created_at')
    search_fields = ('full_name', 'phone_number')
