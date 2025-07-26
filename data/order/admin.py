from django.contrib import admin

from data.order.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'order_type', 'get_or_take', 'comment',
                    'price', "is_installment", "installment_count")

    search_fields = ('customer',)
    list_filter = ('order_type', 'get_or_take', 'created_at')

