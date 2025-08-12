from django.contrib import admin
from data.payment.models import InstallmentPayment, Payment


@admin.register(InstallmentPayment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = ("order", "payment_date", "amount", "left", "created_at")
    search_fields = ("order",)
    list_filter = (
        "payment_date",
        "created_at",
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = ["customer", "payment_type","payment_choice", "amount"]

    list_filter = ["payment_type", "customer"]
