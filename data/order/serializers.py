from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from data.customer.serializers import CustomerSerializer
from data.order.models import Order, OrderFile


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()

    class Meta:
        model = Order
        fields = ('id', 'customer', 'order_type', 'get_or_take', 'comment', 'price')


class OrderFileSerializer(serializers.ModelSerializer):
    order = OrderSerializer()

    class Meta:
        model = OrderFile
        fields = ('id', 'order', 'file')
