from django.db.models import Sum
from rest_framework import serializers
from data.balance.models import Balance
from data.customer.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()
    orders_count = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ('id', 'full_name', 'phone_number', 'get_order', 'balance', 'orders_count')

    def get_balance(self, customer):
        income = Balance.objects.filter(
            customer=customer,
            type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0

        outcome = Balance.objects.filter(
            customer=customer,
            type='outcome'
        ).aggregate(total=Sum('amount'))['total'] or 0

        balance = income - outcome

        return balance

    def get_orders_count(self, customer):
        return customer.orders.count()
