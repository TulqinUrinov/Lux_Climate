from rest_framework import serializers

from data.balance.models import Balance
from data.customer.models import Customer
from data.customer.serializers import CustomerSerializer
from data.payment.models import InstallmentPayment, Payment


class InstallmentPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPayment
        fields = (
            "id",
            "amount",
            "payment_date",
            "created_at",
        )


class PaymentSerializer(serializers.ModelSerializer):

    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())

    class Meta:
        model = Payment
        fields = ["id", "customer", "payment_type", "amount", "created_by"]

    def to_representation(self, instance):
        res = super().to_representation(instance)

        res["customer"] = (
            CustomerSerializer(instance.customer).data if instance.customer else None
        )

        return res


class CustomerOrderPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ("id", "reason", "amount", "created_at")
