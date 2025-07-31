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

        # Foydalanuvchini request'dan olish
        request = self.context.get("request")
        user_id = request.user.id
        user = User.objects.filter(id=user_id).first()

        if order.get_or_give == 'give_order':
            # Biz mijozga mahsulot berdik → hali pul olmadik → chiqim
            Balance.objects.create(
                user=user,
                customer=order.customer,
                amount=order.price,
                reason="order",
                comment=f"Buyurtma berildi",
                type='outcome',
                change=-abs(order.price),
            )

        elif order.get_or_give == 'get_order':
            # Biz mijozdan mahsulot oldik unga + price yoziladi
            Balance.objects.create(
                user=user,
                customer=order.customer,
                amount=order.price,
                reason="order",
                comment=f"Buyurtma olindi",
                type='income',
                change=abs(order.price),
            )

        return order


class OrderListSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'customer', 'order_type', 'price', 'created_at')

    def get_customer(self, obj):
        return obj.customer.full_name


class CustomerOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'order_type', 'price', 'created_at')


# Customer Order Debt
class CustomerOrderDebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ('id', 'reason', 'amount', 'created_at')



class OrderSerializer(serializers.ModelSerializer):
    model = Order
    fields = ('id','customer', 'order_type', 'get_or_give','price',)