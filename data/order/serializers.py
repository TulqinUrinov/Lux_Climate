from rest_framework import serializers

from data.balance.models import Balance
from data.customer.models import Customer
from data.file.models import File
from data.order.models import Order
from data.payment.models import InstallmentPayment
from data.payment.serializers import InstallmentPaymentSerializer
from data.user.models import User


class OrderCreateSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    files = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True)
    order_splits = InstallmentPaymentSerializer(many=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "customer",
            "product",
            "order_type",
            "comment",
            "files",
            "price",
            "is_installment",
            "installment_count",
            "order_splits",
        )

    def create(self, validated_data):
        payments_data = validated_data.pop("order_splits", [])
        files_data = validated_data.pop("files", [])

        order = Order.objects.create(**validated_data)

        # Fayllarni bog'lash
        order.files.set(files_data)

        # To‘lovlarni saqlash
        if order.is_installment:
            for payment_data in payments_data:
                InstallmentPayment.objects.create(order=order, **payment_data)
        else:
            InstallmentPayment.objects.create(
                order=order,
                amount=order.price,
                payment_date=order.created_at,
                left=order.price,
            )

        order.customer.recalculate_balance()

        return order

    def update(self, instance, validated_data):
        payments_data = validated_data.pop("order_splits", [])
        files_data = validated_data.pop("files", [])

        # Order fieldlarini yangilash
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Fayllarni yangilash
        instance.files.set(files_data)

        # Eski to‘lovlarni o‘chirish
        instance.installmentpayment_set.all().delete()

        # Yangi to‘lovlarni yozish
        if instance.is_installment:
            for payment_data in payments_data:
                InstallmentPayment.objects.create(order=instance, **payment_data)
        else:
            InstallmentPayment.objects.create(
                order=instance,
                amount=instance.price,
                payment_date=instance.created_at,
                left=instance.price,
            )

        instance.customer.recalculate_balance()

        return instance


class OrderListSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ("id", "customer", "product", "order_type", "price", "created_at")

    def get_customer(self, obj):
        return obj.customer.full_name


class CustomerOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "order_type", "product", "price", "created_at")


class CustomerOrderDebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPayment
        fields = ('id', 'left', 'amount', 'left', 'payment_date')


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    order_splits = InstallmentPaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "customer",
            "order_type",
            "order_type",
            "price",
            "created_at",
            "is_installment",
            "installment_count",
            "order_splits",
        )

    def get_customer(self, obj):
        return obj.customer.full_name
