from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils.dateparse import parse_date
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.response import Response

from data.bot.permission import IsBotAuthenticated
from data.common.pagination import CustomPagination
from data.customer.models import Customer
from data.payment.models import InstallmentPayment, Payment
from data.payment.send_message import send_payment_to_customer
from data.payment.serializers import (
    InstallmentPaymentSerializer,
    PaymentSerializer,
)


class PaymentListCreateView(ListCreateAPIView):
    permission_classes = [IsBotAuthenticated]
    pagination_class = CustomPagination

    serializer_class = PaymentSerializer

    def get_queryset(self):

        if self.request.role == "ADMIN":

            queryset = Payment.objects.all().order_by("-created_at")

            payment_choice = self.request.query_params.get("payment_choice")
            customer_id = self.request.query_params.get("customer_id")
            start_date = self.request.query_params.get("start_date")
            end_date = self.request.query_params.get("end_date")

            if customer_id:
                queryset = queryset.filter(customer_id=customer_id).all()

            # to'lov turi bo'yicha filter qilib beradi
            if payment_choice:
                queryset = queryset.filter(payment_choice=payment_choice).all()

            if start_date:
                queryset = queryset.filter(created_at__gte=parse_date(start_date))

            if end_date:
                queryset = queryset.filter(created_at__lte=parse_date(end_date))

            return queryset

        customer: Customer = self.request.customer
        queryset = customer.payments.all().order_by("-created_at")

        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(created_at__date__gte=parse_date(start_date))

        if end_date:
            queryset = queryset.filter(created_at__date__lte=parse_date(end_date))

        return queryset

    def perform_create(self, serializer: PaymentSerializer):
        payment = serializer.save(created_by=self.request.admin)
        send_payment_to_customer(payment)

    @staticmethod
    def transfer_between_choices(customer, from_choice, to_choice, amount, created_by):
        from_balance = customer.balances.filter(payment_choice=from_choice) \
                           .aggregate(total=Sum("change"))["total"] or Decimal("0")

        print(f"Balance:{from_balance}")
        print(f"Amount:{amount}")


        if from_balance < amount:
            raise ValidationError(f"{from_choice} balansida yetarli mablag' yo'q!")

        with transaction.atomic():
            # OUTCOME yozuvi
            Payment.objects.create(
                customer=customer,
                payment_type="COMPANY_TO_CUSTOMER",
                payment_choice=from_choice,
                payment_method="INTERNAL_TRANSFER",
                amount=amount,
                comment=f"{from_choice} → {to_choice} o'tkazma",
                created_by=created_by
            )

            # INCOME yozuvi
            Payment.objects.create(
                customer=customer,
                payment_type="CUSTOMER_TO_COMPANY",
                payment_choice=to_choice,
                payment_method="INTERNAL_TRANSFER",
                amount=amount,
                comment=f"{from_choice} → {to_choice} o'tkazma",
                created_by=created_by
            )

            customer.recalculate_balance()

    def post(self, request, *args, **kwargs):
        # Agar transfer bo'lsa
        if "from_choice" in request.data and "to_choice" in request.data:
            customer = Customer.objects.get(id=request.data["customer_id"])
            self.transfer_between_choices(
                customer=customer,
                from_choice=request.data["from_choice"],
                to_choice=request.data["to_choice"],
                amount=Decimal(request.data["amount"]),
                created_by=request.admin
            )
            return Response({"detail": "O'tkazma amalga oshirildi"})

        # Oddiy payment bo'lsa DRF oqimini ishlatish
        return super().post(request, *args, **kwargs)


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
        queryset = InstallmentPayment.objects.all().order_by("-created_at")

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

        elif status == "partial":
            queryset = queryset.filter(left__gt=0)

        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        today = date.today()
        modified_data = []

        for item in response.data["results"]:
            payment_date = item.get("payment_date")
            left = float(item.get("left", 0))

            # Status aniqlash
            if left == 0:
                status = "paid"
            elif payment_date < str(today):
                status = "overdue"
            else:
                status = "not_due"

            item["status"] = status
            modified_data.append(item)

        response.data["results"] = modified_data
        return response
