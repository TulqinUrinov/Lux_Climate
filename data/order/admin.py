from django.contrib import admin

from data.order.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "order_type",
        "order_type",
        "comment",
        "price",
        "show_files",
        "is_installment",
        "installment_count",
    )

    search_fields = ("customer",)
    list_filter = (
        "order_type",
        "order_type",
        "created_at",
    )

    def show_files(self, obj):
        return ", ".join(
            [str(file) for file in obj.files.all()]
        )  # yoki file.name agar `__str__` yo'q bo'lsa

    show_files.short_description = "Files"
