from rest_framework import serializers
from data.balance.models import Balance
from data.customer.models import Customer
from data.file.models import File
from data.file.serializers import FileSerializer
from data.order.models import Order
from data.payment.models import InstallmentPayment
from data.payment.serializers import InstallmentPaymentSerializer
from data.user.models import User


class InstallmentPaymentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPayment
        exclude = ("id", "created_at", "order", "customer", "order_type")


class OrderCreateUpdateSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    files = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True)
    order_splits = InstallmentPaymentWriteSerializer(many=True)

    # order_splits = InstallmentPaymentSerializer(many=True)

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
            "usd_course",
            "usd_amount",
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

            if payments_data:  # frontend yuborgan bo‘lsa
                payment_date = payments_data[0].get("payment_date")
            else:
                payment_date = order.created_at  # fallback, agar yuborilmasa

            InstallmentPayment.objects.create(
                order=order,
                amount=order.price,
                # payment_date=order.created_at,
                payment_date=payment_date,
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
        instance.order_splits.all().delete()

        # Yangi to‘lovlarni yozish
        if instance.is_installment:
            for payment_data in payments_data:
                InstallmentPayment.objects.create(order=instance, **payment_data)
        else:

            if payments_data:  # frontend yuborgan bo‘lsa
                payment_date = payments_data[0].get("payment_date")
            else:
                payment_date = instance.created_at  # fallback

            InstallmentPayment.objects.create(
                order=instance,
                amount=instance.price,
                # payment_date=instance.created_at,
                payment_date=payment_date,
                left=instance.price,
            )

        instance.customer.recalculate_balance()

        return instance


# Barcha buyurtmalar ro'yxati
class OrderListSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ("id", "customer", "product", "order_type", "price", "usd_course", "usd_amount", "created_at")

    def get_customer(self, obj):
        return obj.customer.full_name


# Faqat 1 ta buyurtma uchun
class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    order_splits = InstallmentPaymentSerializer(many=True, read_only=True)
    files = FileSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "customer",
            "product",
            "order_type",
            "price",
            "usd_course",
            "usd_amount",
            "created_at",
            "is_installment",
            "installment_count",
            "files",
            "order_splits",
        )

    def get_customer(self, obj):
        return {
            "id": obj.customer.id,
            "full_name": obj.customer.full_name,
        }
