from datetime import datetime, time
from django.db.models import Sum
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import mutual_settlements
from .serializers import *
from ..bot.permission import IsBotAuthenticated
from ..order.models import Order
from ..payment.models import InstallmentPayment
from django.db.models import Sum, Case, When, DecimalField, Q, F, Value
from decimal import Decimal


class MutualSettlementView(APIView):
    permission_classes = [IsBotAuthenticated]

    def get(self, request, customer_id):
        settlements = mutual_settlements(self, customer_id=customer_id, last_one=False)

        if not settlements:
            return Response(
                {"detail": "Ma'lumot topilmadi"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = MutualSettlementSerializer(settlements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Umumiy Statistika
class BalanceStatusView(APIView):
    permission_classes = [IsBotAuthenticated]

    def get(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        # Umumiy (filternatsiya qilinmagan) income va outcome
        total_income = (
                Balance.objects.filter(type="INCOME").aggregate(
                    total=Sum("amount"))["total"] or 0
        )

        total_product_income = (
                Balance.objects.filter(type="INCOME", payment_choice="PRODUCT").aggregate(
                    total=Sum("amount"))["total"] or 0
        )

        total_service_income = (
                Balance.objects.filter(type="INCOME", payment_choice="SERVICE").aggregate(
                    total=Sum("amount"))["total"] or 0
        )

        total_outcome = (
                Balance.objects.filter(type="OUTCOME").aggregate(
                    total=Sum("amount"))["total"] or 0
        )

        total_product_outcome = (
                Balance.objects.filter(type="OUTCOME", payment_choice="PRODUCT").aggregate(
                    total=Sum("amount"))["total"] or 0
        )

        total_service_outcome = (
                Balance.objects.filter(type="OUTCOME", payment_choice="SERVICE").aggregate(
                    total=Sum("amount"))["total"] or 0
        )

        start_datetime = None
        end_datetime = None

        try:
            if start_date:
                start_datetime = datetime.combine(
                    datetime.strptime(start_date, "%Y-%m-%d"), time.min
                )
            if end_date:
                end_datetime = datetime.combine(
                    datetime.strptime(end_date, "%Y-%m-%d"), time.max
                )
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if start_datetime and end_datetime:
            # Buyurtmalarning umumiy soni
            orders = Order.objects.filter(
                created_at__range=[start_datetime, end_datetime]
            ).count()

            # Buyurtmalarning product bo'yicha soni
            product_orders = Order.objects.filter(
                product="PRODUCT",
                created_at__range=[start_datetime, end_datetime]
            ).count()

            # Buyurtmalarning service bo'yicha soni
            service_orders = Order.objects.filter(
                product="SERVICE",
                created_at__range=[start_datetime, end_datetime]
            ).count()

            # Barcha buyurtmalarning umumiy narxi
            orders_sum_price = (
                    Order.objects.filter(
                        created_at__range=[start_datetime, end_datetime]
                    ).aggregate(total=Sum("price"))["total"]
                    or 0
            )

            # PRODUCT bo'yicha buyurtmalarning umumiy narxi
            product_orders_sum_price = (
                    Order.objects.filter(
                        product="PRODUCT",
                        created_at__range=[start_datetime, end_datetime]
                    ).aggregate(total=Sum("price"))["total"]
                    or 0
            )

            # SERVICE bo'yicha buyurtmalarning umumiy narxi
            service_orders_sum_price = (
                    Order.objects.filter(
                        product="SERVICE",
                        created_at__range=[start_datetime, end_datetime]
                    ).aggregate(total=Sum("price"))["total"]
                    or 0
            )

            # Sana bo'yicha filter qilingan umumiy kirim
            filtered_income = (
                    Balance.objects.filter(
                        type="INCOME", created_at__range=[start_datetime, end_datetime]
                    ).aggregate(total=Sum("amount"))["total"]
                    or 0
            )

            # PRODUCT, Sana bo'yicha filter qilingan umumiy kirim
            product_filtered_income = (
                    Balance.objects.filter(
                        payment_choice="PRODUCT",
                        type="INCOME",
                        created_at__range=[start_datetime, end_datetime]
                    ).aggregate(total=Sum("amount"))["total"]
                    or 0
            )

            # SERVICE, Sana bo'yicha filter qilingan umumiy kirim
            service_filtered_income = (
                    Balance.objects.filter(
                        payment_choice="SERVICE",
                        type="INCOME",
                        created_at__range=[start_datetime, end_datetime]
                    ).aggregate(total=Sum("amount"))["total"]
                    or 0
            )

            # Sana bo'yicha filter qilingan umumiy chiqim
            filtered_outcome = (
                    Balance.objects.filter(
                        type="OUTCOME", created_at__range=[start_datetime, end_datetime]
                    ).aggregate(total=Sum("amount"))["total"]
                    or 0
            )

            # PRODUCT, Sana bo'yicha filter qilingan umumiy chiqim
            product_filtered_outcome = (
                    Balance.objects.filter(
                        payment_choice="PRODUCT",
                        type="OUTCOME",
                        created_at__range=[start_datetime, end_datetime]
                    ).aggregate(total=Sum("amount"))["total"]
                    or 0
            )

            # SERVICE, Sana bo'yicha filter qilingan umumiy chiqim
            service_filtered_outcome = (
                    Balance.objects.filter(
                        payment_choice="SERVICE",
                        type="OUTCOME",
                        created_at__range=[start_datetime, end_datetime]
                    ).aggregate(total=Sum("amount"))["total"]
                    or 0
            )

            # Umumiy to'lanishi kerak bo'lgan to'lov
            due_payment = filtered_outcome - filtered_income

            # PRODUCT bo'yicha umumiy to'lanishi kerak bo'lgan to'lov
            product_due_payment = product_filtered_outcome - product_filtered_income

            # SERVICE bo'yicha umumiy to'lanishi kerak bo'lgan to'lov
            service_due_payment = service_filtered_outcome - service_filtered_income

        else:
            # Buyurtmalar umumiy soni
            orders = Order.objects.count()

            # Buyurtmalarning product bo'yicha soni
            product_orders = Order.objects.filter(
                product="PRODUCT"
            ).count()

            # Buyurtmalarning service bo'yicha soni
            service_orders = Order.objects.filter(
                product="SERVICE"
            ).count()

            # Barcha buyurtmalarning umumiy narxi
            orders_sum_price = Order.objects.aggregate(total=Sum("price"))["total"] or 0

            # PRODUCT bo'yicha buyurtmalarning umumiy narxi
            product_orders_sum_price = Order.objects.filter(
                product="PRODUCT"
            ).aggregate(total=Sum("price"))["total"] or 0

            # SERVICE bo'yicha buyurtmalarning umumiy narxi
            service_orders_sum_price = Order.objects.filter(
                product="SERVICE"
            ).aggregate(total=Sum("price"))["total"] or 0

            # Umumiy to'lanishi kerak bo'lgan to'lov
            due_payment = total_outcome - total_income

            # PRODUCT bo'yicha umumiy to'lanishi kerak bo'lgan to'lov
            product_due_payment = total_product_outcome - total_product_income

            # SERVICE bo'yicha umumiy to'lanishi kerak bo'lgan to'lov
            service_due_payment = total_service_outcome - total_service_income

            # Umumiy to'lov
            filtered_income = total_income

            # PRODUCT bo'yicha umumiy to'lov
            product_filtered_income = total_product_income

            # SERVICE bo'yicha umumiy to'lov
            service_filtered_income = total_service_income

        # customer_debt = total_income - total_outcome  # Customer umumiy qarzi
        # customer_product_debt = total_product_income - total_product_outcome  # customer mahsulot bo'yicha qarzi
        # customer_service_debt = total_service_income - total_service_outcome  # customer xizmat bo'yicha qarzi

        # user_debt = total_outcome - total_income
        # user_product_debt = total_product_outcome - total_product_income
        # user_service_debt = total_service_outcome - total_service_income

        # --- BALANCE BO‘YICHA UMUMIY DEBT HISOBLASH ---
        balances = (
            Balance.objects.values("customer", "payment_choice")
            .annotate(total_change=Sum("change"))
        )

        # Boshlang‘ich qiymatlar
        customer_debt = Decimal("0")
        user_debt = Decimal("0")
        customer_product_debt = Decimal("0")
        customer_service_debt = Decimal("0")
        user_product_debt = Decimal("0")
        user_service_debt = Decimal("0")

        for b in balances:
            total = b["total_change"] or Decimal("0")
            payment_choice = b["payment_choice"]

            if total < 0:
                # Mijoz qarzi (– balance)
                customer_debt += abs(total)
                if payment_choice == "PRODUCT":
                    customer_product_debt += abs(total)
                elif payment_choice == "SERVICE":
                    customer_service_debt += abs(total)
            elif total > 0:
                # Kompaniya qarzi (+ balance)
                user_debt += total
                if payment_choice == "PRODUCT":
                    user_product_debt += total
                elif payment_choice == "SERVICE":
                    user_service_debt += total

        return Response(
            {
                # Mijoz qarzi
                # "customer_debt": customer_debt if customer_debt < 0 else 0,
                # "customer_product_debt": customer_product_debt if customer_product_debt < 0 else 0,
                # "customer_service_debt": customer_service_debt if customer_service_debt < 0 else 0,

                "customer_debt": customer_debt,
                "customer_product_debt": customer_product_debt,
                "customer_service_debt": customer_service_debt,

                # Admin qarzi
                # "user_debt": user_debt if user_debt < 0 else 0,
                # "user_product_debt": user_product_debt if user_product_debt < 0 else 0,
                # "user_service_debt": user_service_debt if user_service_debt < 0 else 0,

                "user_debt": user_debt,
                "user_product_debt": user_product_debt,
                "user_service_debt": user_service_debt,

                # Buyurtmalar soni
                "orders_count": orders,
                "product_orders_count": product_orders,
                "service_orders_count": service_orders,

                # Umumiy buyurtmalar narxi
                "orders_sum_price": orders_sum_price,
                "product_orders_sum_price": product_orders_sum_price,
                "service_orders_sum_price": service_orders_sum_price,

                # To'lovlar
                "income": filtered_income,
                "product_income": product_filtered_income,
                "service_income": service_filtered_income,

                # Kutilayotgan to'lovlar
                "due_payment": customer_debt,
                "product_due_payment": customer_product_debt,
                "service_due_payment": customer_service_debt,
            },
            status=status.HTTP_200_OK,
        )
