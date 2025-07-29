from rest_framework import serializers

from data.balance.models import Balance
from data.customer.models import Customer
from data.user.models import User


class BalanceSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())

    class Meta:
        model = Balance
        fields = ('user', 'customer', 'payment_date', 'amount', 'reason', 'comment', 'change', 'type')
        read_only_fields = ('change',)


class MutualSettlementSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    customer_id = serializers.IntegerField()
    start_balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    change = serializers.DecimalField(max_digits=10, decimal_places=2)
    final_balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    created_at = serializers.DateTimeField()
    reason = serializers.CharField()
    comment = serializers.CharField()
