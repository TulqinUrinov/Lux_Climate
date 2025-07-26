from django.contrib import admin
from data.payment.models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'order', 'pay_date', 'amount')
    search_fields = ('customer','order')
    list_filter = ('pay_date', )
