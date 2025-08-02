from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from data.common.pagination import CustomPagination
from data.customer.models import Customer
from data.payment.models import Payment
from data.payment.serializers import PaymentSerializer, CustomerOrderPaymentSerializer


class PaymentListView(ListCreateAPIView):

    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    serializer_class = PaymentSerializer

    def get_queryset(self):

        if self.request.role == "ADMIN":
            return Payment.objects.all()

        customer: Customer = self.request.customer

        return customer.payments.all()

    def perform_create(self, serializer: PaymentSerializer):

        serializer.save(created_by=self.request.admin)
