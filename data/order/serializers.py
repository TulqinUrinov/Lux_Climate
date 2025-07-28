from rest_framework import serializers
from data.customer.models import Customer
from data.file.models import File
from data.order.models import Order
from data.payment.models import InstallmentPayment
from data.payment.serializers import InstallmentPaymentSerializer


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    files = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True)
    installment_payments = InstallmentPaymentSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'customer', 'order_type', 'get_or_give', 'comment', 'files',
                  'price', 'is_installment', 'installment_count', 'installment_payments')

    def create(self, validated_data):
        payments_data = validated_data.pop('installment_payments', [])
        files_data = validated_data.pop('files', [])

        order = Order.objects.create(**validated_data)

        # Fayllarni bog'lash
        order.files.set(files_data)

        # To‘lovlarni saqlash
        for payment_data in payments_data:
            InstallmentPayment.objects.create(order=order, **payment_data)

        return order



class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'customer', 'order_type', 'price', 'created_at')
