from rest_framework import serializers
from data.customer.models import Customer
from data.file.models import File
from data.order.models import Order
from data.installmentpayment.models import InstallmentPayment
from data.installmentpayment.serializers import PaymentSerializer


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    files = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True)
    payment = PaymentSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'customer', 'order_type', 'get_or_take', 'comment', 'files',
                  'price', 'is_installment', 'installment_count', 'installmentpayment')

    def create(self, validated_data):
        payments_data = validated_data.pop('payments', [])
        order = Order.objects.create(**validated_data)

        # To‘lovlarni saqlash
        for payment_data in payments_data:
            InstallmentPayment.objects.create(order=order,
                                              customer=order.customer,
                                              **payment_data)
        return order
