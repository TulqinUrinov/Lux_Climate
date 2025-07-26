from rest_framework import serializers
from data.customer.models import Customer
from data.order.models import Order, OrderFile
from data.payment.models import Payment
from data.payment.serializers import PaymentSerializer


class OrderFileSerializer(serializers.ModelSerializer):
    # order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    class Meta:
        model = OrderFile
        fields = ('id',)


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    order_files = OrderFileSerializer(many=True)
    payment = PaymentSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'customer', 'order_type', 'get_or_take', 'comment', 'order_files',
                  'price', 'is_installment', 'installment_count', 'payment')

    def create(self, validated_data):
        order_files_data = validated_data.pop('order_files', [])
        payments_data = validated_data.pop('payments', [])

        order = Order.objects.create(**validated_data)

        # Fayllarni saqlash
        for file_data in order_files_data:
            OrderFile.objects.create(order=order, **file_data)

        # To‘lovlarni saqlash
        for payment_data in payments_data:
            Payment.objects.create(order=order,
                                   customer=order.customer,
                                   **payment_data)
        return order
