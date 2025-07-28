from rest_framework import serializers

from data.balance.models import Balance
from data.customer.models import Customer
from data.order.models import Order


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'full_name', 'phone_number', 'get_order')


# Customer orders
class CustomerOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'order_type', 'price', 'created_at')


# Customer order Payment
class CustomerOrderPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ('id', 'reason', 'amount', 'created_at')


# Customer Order Debt
class CustomerOrderDebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ('id', 'reason', 'amount', 'created_at')
