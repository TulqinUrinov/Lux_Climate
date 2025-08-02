from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from data.common.pagination import CustomPagination
from data.customer.models import Customer
from data.payment.models import InstallmentPayment, Payment
from data.payment.serializers import (
    InstallmentPaymentSerializer,
    PaymentSerializer,
    CustomerOrderPaymentSerializer,
)


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


class DebtSplitsListAPIView(ListAPIView):

    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    serializer_class = InstallmentPaymentSerializer

    def get_queryset(self):
        if self.request.role == "CUSTOMER":
            return self.request.customer.order_splits.filter(left__gt=0)

        # Assuming role is ADMIN (or something else allowed)
        queryset = InstallmentPayment.objects.filter(left__gt=0)

        customer_id = self.request.GET.get("customer")

        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        return queryset
