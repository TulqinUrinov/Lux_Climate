from django.contrib import admin
from data.installmentpayment.models import InstallmentPayment

@admin.register(InstallmentPayment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_date', 'amount')
    search_fields = ('order',)
    list_filter = ('payment_date', )
