from datetime import date

from rest_framework.generics import ListAPIView, ListCreateAPIView

from data.bot.permission import IsBotAuthenticated
from data.common.pagination import CustomPagination
from data.customer.models import Customer
from data.payment.models import InstallmentPayment, Payment
from data.payment.serializers import (
    InstallmentPaymentSerializer,
    PaymentSerializer,
    CustomerOrderPaymentSerializer,
)


class PaymentListView(ListCreateAPIView):
    permission_classes = [IsBotAuthenticated]
    pagination_class = CustomPagination

    serializer_class = PaymentSerializer

    def get_queryset(self):
        if self.request.role == "ADMIN":
            customer_id = self.request.query_params.get("customer_id")

            if customer_id:
                return Payment.objects.filter(customer_id=customer_id).all()

            return Payment.objects.all()

        customer: Customer = self.request.customer

        return customer.payments.all()

    def perform_create(self, serializer: PaymentSerializer):
        serializer.save(created_by=self.request.admin)


class DebtSplitsListAPIView(ListAPIView):
    permission_classes = [IsBotAuthenticated]
    pagination_class = CustomPagination

    serializer_class = InstallmentPaymentSerializer

    def get_queryset(self):

        today = date.today()

        status = self.request.GET.get("status")

        if self.request.role == "CUSTOMER":
            return self.request.customer.order_splits.filter(left__gt=0)


        # Assuming role is ADMIN (or something else allowed)
        # queryset = InstallmentPayment.objects.filter(left__gt=0)
        queryset = InstallmentPayment.objects.all()

        customer_id = self.request.GET.get("customer")

        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        # To'langan
        if status == "paid":
            queryset = queryset.filter(left=0)

        # To'lanmagan va muddati o'tgan
        elif status == "overdue":
            queryset = queryset.filter(left__gt=0, payment_date__lt=today)

        # To'lanmagan va muddati hali kelmagan
        elif status == "not_due":
            queryset = queryset.filter(left__gt=0, payment_date__gte=today)

        return queryset
