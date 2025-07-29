from rest_framework import serializers

from data.balance.models import Balance
from data.customer.models import Customer
from data.order.models import Order


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'full_name', 'phone_number', 'get_order')

