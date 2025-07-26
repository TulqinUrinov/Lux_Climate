from rest_framework import serializers
from data.payment.models import InstallmentPayment


class InstallmentPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPayment
        fields = ('id', 'amount', 'payment_date')
