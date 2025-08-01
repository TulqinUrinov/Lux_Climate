from rest_framework import serializers

from data.balance.models import Balance
from data.payment.models import InstallmentPayment


class InstallmentPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPayment
        fields = ('id', 'amount','payment_date','created_at',)


class PaymentSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()

    class Meta:
        model = Balance
        fields = ('id', 'customer', 'reason', 'amount', 'created_at',)

    def get_customer(self, obj):
        return obj.customer.full_name


class CustomerOrderPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ('id', 'reason', 'amount', 'created_at')
