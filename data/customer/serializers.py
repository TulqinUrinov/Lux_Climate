from decimal import Decimal

from django.db.models import Sum
from rest_framework import serializers
from data.balance.models import Balance
from data.customer.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    orders_count = serializers.SerializerMethodField()
    product_balance = serializers.SerializerMethodField()
    service_balance = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = (
            "id",
            "full_name",
            "phone_number",
            "get_order",
            "is_archived",
            "balance",
            "product_balance",
            "service_balance",
            "orders_count",
        )

    # def get_balance(self, customer):
    #     income = Balance.objects.filter(
    #         customer=customer,
    #         type='income'
    #     ).aggregate(total=Sum('amount'))['total'] or 0

    #     outcome = Balance.objects.filter(
    #         customer=customer,
    #         type='outcome'
    #     ).aggregate(total=Sum('amount'))['total'] or 0

    #     balance = income - outcome

    #     return balance

    def get_orders_count(self, customer):
        return customer.orders.count()

    def get_product_balance(self, obj: Customer):
        product_balance = obj.balances.filter(type="PRODUCT").aggregate(
            total=Sum("change")
        )["total"] or Decimal("0.00")

        return product_balance

    def get_service_balance(self, obj: Customer):
        service_balance = obj.balances.filter(type="SERVICE").aggregate(
            total=Sum("change")
        )["total"] or Decimal("0.00")

        return service_balance
