from rest_framework import serializers

from data.balance.models import Balance
from data.payment.models import InstallmentPayment


class InstallmentPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPayment
        fields = ('id', 'amount', 'payment_date')


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ('id', 'customer', 'reason', 'amount', 'created_at',)


class CustomerOrderPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ('id', 'reason', 'amount', 'created_at')
