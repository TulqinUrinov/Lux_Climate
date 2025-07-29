
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from data.balance.models import Balance
from data.payment.serializers import PaymentSerializer, CustomerOrderPaymentSerializer


class PaymentListView(ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            return Balance.objects.filter(type='income', customer_id=customer_id)
        return Balance.objects.filter(type='income')

    def get_serializer_class(self):
        if self.request.query_params.get('customer_id'):
            return CustomerOrderPaymentSerializer
        return PaymentSerializer