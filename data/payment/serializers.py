from rest_framework import serializers

from data.customer.models import Customer
from data.customer.serializers import CustomerSerializer
from data.payment.models import InstallmentPayment, Payment


class InstallmentPaymentSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()

    class Meta:
        model = InstallmentPayment
        fields = (
            "id",
            "amount",
            "order",
            "order_type",
            "payment_date",
            "left",
            "created_at",
            "customer",
        )

    def get_customer(self, obj):
        return obj.customer.full_name


class PaymentSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id",
            "customer",
            "payment_type",
            "payment_method",
            "amount",
            "created_by",
            "created_at",
        ]

    def get_created_by(self, obj):
        return obj.created_by.full_name

    def to_representation(self, instance):
        res = super().to_representation(instance)

        res["customer"] = (
            CustomerSerializer(instance.customer).data if instance.customer else None
        )

        return res
