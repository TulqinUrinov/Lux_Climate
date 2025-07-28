from django.contrib import admin
from .models import Balance
from .services import mutual_settlements

@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "payment_date",
        "user",
        "customer",
        "type",
        "reason",
        "get_start_balance",
        "change",
        "get_final_balance",
        "comment",
    )
    list_filter = ("type", "reason", "payment_date", "user", "customer")
    search_fields = ("user__full_name", "customer__full_name", "comment")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        self.balances_map = {}

        # Barcha mijozlar uchun balanslar jadvalini tuzamiz
        for customer_id in qs.values_list("customer_id", flat=True).distinct():
            records = mutual_settlements(self, customer_id=customer_id)
            for record in records:
                self.balances_map[record["id"]] = {
                    "start_balance": record["start_balance"],
                    "final_balance": record["final_balance"]
                }
        return qs

    @admin.display(description="Start Balance")
    def get_start_balance(self, obj):
        data = self.balances_map.get(obj.id, {})
        return data.get("start_balance", "-")

    @admin.display(description="Final Balance")
    def get_final_balance(self, obj):
        data = self.balances_map.get(obj.id, {})
        return data.get("final_balance", "-")
