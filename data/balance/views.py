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


class BalanceStatusView(APIView):
    permission_classes = [IsBotAuthenticated]

    def get(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        start, end = None, None
        try:
            if start_date:
                start = datetime.combine(datetime.strptime(start_date, "%Y-%m-%d"), time.min)
            if end_date:
                end = datetime.combine(datetime.strptime(end_date, "%Y-%m-%d"), time.max)
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Balanslar
        total_income = balance_sum("INCOME", start=start, end=end)
        total_outcome = balance_sum("OUTCOME", start=start, end=end)

        product_income = balance_sum("INCOME", "PRODUCT", start, end)
        service_income = balance_sum("INCOME", "SERVICE", start, end)

        product_outcome = balance_sum("OUTCOME", "PRODUCT", start, end)
        service_outcome = balance_sum("OUTCOME", "SERVICE", start, end)

        # Buyurtmalar
        all_orders = order_stats(start=start, end=end)
        product_orders = order_stats("PRODUCT", start, end)
        service_orders = order_stats("SERVICE", start, end)

        # Qarzdorlik
        customer_debt = total_income - total_outcome
        user_debt = total_outcome - total_income

        return Response({
            # Qarzdorlik
            "customer_debt": min(customer_debt, 0),
            "customer_product_debt": min(product_income - product_outcome, 0),
            "customer_service_debt": min(service_income - service_outcome, 0),

            "user_debt": min(user_debt, 0),
            "user_product_debt": min(product_outcome - product_income, 0),
            "user_service_debt": min(service_outcome - service_income, 0),

            # Buyurtmalar
            "orders_count": all_orders["count"],
            "product_orders_count": product_orders["count"],
            "service_orders_count": service_orders["count"],

            "orders_sum_price": all_orders["sum_price"],
            "product_orders_sum_price": product_orders["sum_price"],
            "service_orders_sum_price": service_orders["sum_price"],

            # To‘lovlar
            "income": total_income,
            "product_income": product_income,
            "service_income": service_income,

            # Kutilayotgan to‘lovlar
            "due_payment": max(total_outcome - total_income, 0),
            "product_due_payment": max(product_outcome - product_income, 0),
            "service_due_payment": max(service_outcome - service_income, 0),
        })


def get_sum(queryset, field="amount"):
    return queryset.aggregate(total=Sum(field))["total"] or 0


def balance_sum(balance_type, choice=None, start=None, end=None):
    filters = {"type": balance_type}
    if choice:
        filters["payment_choice"] = choice
    if start and end:
        filters["created_at__range"] = [start, end]
    return get_sum(Balance.objects.filter(**filters))


def order_stats(product=None, start=None, end=None):
    filters = {}
    if product:
        filters["product"] = product
    if start and end:
        filters["created_at__range"] = [start, end]

    qs = Order.objects.filter(**filters)
    return {
        "count": qs.count(),
        "sum_price": get_sum(qs, "price")
    }

# class BalanceStatusView(APIView):
#     permission_classes = [IsBotAuthenticated]
#
#     def get(self, request):
#         start_date = request.query_params.get("start_date")
#         end_date = request.query_params.get("end_date")
#
#         # Umumiy (filternatsiya qilinmagan) income va outcome
#         total_income = (
#                 Balance.objects.filter(type="INCOME").aggregate(
#                     total=Sum("amount"))["total"] or 0
#         )
#
#         total_product_income = (
#                 Balance.objects.filter(type="INCOME", payment_choice="PRODUCT").aggregate(
#                     total=Sum("amount"))["total"] or 0
#         )
#
#         total_service_income = (
#                 Balance.objects.filter(type="INCOME", payment_choice="SERVICE").aggregate(
#                     total=Sum("amount"))["total"] or 0
#         )
#
#         total_outcome = (
#                 Balance.objects.filter(type="OUTCOME").aggregate(
#                     total=Sum("amount"))["total"] or 0
#         )
#
#         total_product_outcome = (
#                 Balance.objects.filter(type="OUTCOME", payment_choice="PRODUCT").aggregate(
#                     total=Sum("amount"))["total"] or 0
#         )
#
#         total_service_outcome = (
#                 Balance.objects.filter(type="OUTCOME", payment_choice="SERVICE").aggregate(
#                     total=Sum("amount"))["total"] or 0
#         )
#
#         start_datetime = None
#         end_datetime = None
#
#         try:
#             if start_date:
#                 start_datetime = datetime.combine(
#                     datetime.strptime(start_date, "%Y-%m-%d"), time.min
#                 )
#             if end_date:
#                 end_datetime = datetime.combine(
#                     datetime.strptime(end_date, "%Y-%m-%d"), time.max
#                 )
#         except ValueError:
#             return Response(
#                 {"error": "Invalid date format. Use YYYY-MM-DD"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#
#         if start_datetime and end_datetime:
#             # Buyurtmalarning umumiy soni
#             orders = Order.objects.filter(
#                 created_at__range=[start_datetime, end_datetime]
#             ).count()
#
#             # Buyurtmalarning product bo'yicha soni
#             product_orders = Order.objects.filter(
#                 product="PRODUCT",
#                 created_at__range=[start_datetime, end_datetime]
#             ).count()
#
#             # Buyurtmalarning service bo'yicha soni
#             service_orders = Order.objects.filter(
#                 product="SERVICE",
#                 created_at__range=[start_datetime, end_datetime]
#             ).count()
#
#             # Barcha buyurtmalarning umumiy narxi
#             orders_sum_price = (
#                     Order.objects.filter(
#                         created_at__range=[start_datetime, end_datetime]
#                     ).aggregate(total=Sum("price"))["total"]
#                     or 0
#             )
#
#             # PRODUCT bo'yicha buyurtmalarning umumiy narxi
#             product_orders_sum_price = (
#                     Order.objects.filter(
#                         product="PRODUCT",
#                         created_at__range=[start_datetime, end_datetime]
#                     ).aggregate(total=Sum("price"))["total"]
#                     or 0
#             )
#
#             # SERVICE bo'yicha buyurtmalarning umumiy narxi
#             service_orders_sum_price = (
#                     Order.objects.filter(
#                         product="SERVICE",
#                         created_at__range=[start_datetime, end_datetime]
#                     ).aggregate(total=Sum("price"))["total"]
#                     or 0
#             )
#
#             # Sana bo'yicha filter qilingan umumiy kirim
#             filtered_income = (
#                     Balance.objects.filter(
#                         type="INCOME", created_at__range=[start_datetime, end_datetime]
#                     ).aggregate(total=Sum("amount"))["total"]
#                     or 0
#             )
#
#             # PRODUCT, Sana bo'yicha filter qilingan umumiy kirim
#             product_filtered_income = (
#                     Balance.objects.filter(
#                         payment_choice="PRODUCT",
#                         type="INCOME",
#                         created_at__range=[start_datetime, end_datetime]
#                     ).aggregate(total=Sum("amount"))["total"]
#                     or 0
#             )
#
#             # SERVICE, Sana bo'yicha filter qilingan umumiy kirim
#             service_filtered_income = (
#                     Balance.objects.filter(
#                         payment_choice="SERVICE",
#                         type="INCOME",
#                         created_at__range=[start_datetime, end_datetime]
#                     ).aggregate(total=Sum("amount"))["total"]
#                     or 0
#             )
#
#             # Sana bo'yicha filter qilingan umumiy chiqim
#             filtered_outcome = (
#                     Balance.objects.filter(
#                         type="OUTCOME", created_at__range=[start_datetime, end_datetime]
#                     ).aggregate(total=Sum("amount"))["total"]
#                     or 0
#             )
#
#             # PRODUCT, Sana bo'yicha filter qilingan umumiy chiqim
#             product_filtered_outcome = (
#                     Balance.objects.filter(
#                         payment_choice="PRODUCT",
#                         type="OUTCOME",
#                         created_at__range=[start_datetime, end_datetime]
#                     ).aggregate(total=Sum("amount"))["total"]
#                     or 0
#             )
#
#             # SERVICE, Sana bo'yicha filter qilingan umumiy chiqim
#             service_filtered_outcome = (
#                     Balance.objects.filter(
#                         payment_choice="SERVICE",
#                         type="OUTCOME",
#                         created_at__range=[start_datetime, end_datetime]
#                     ).aggregate(total=Sum("amount"))["total"]
#                     or 0
#             )
#
#             # Umumiy to'lanishi kerak bo'lgan to'lov
#             due_payment = filtered_outcome - filtered_income
#
#             # PRODUCT bo'yicha umumiy to'lanishi kerak bo'lgan to'lov
#             product_due_payment = product_filtered_outcome - product_filtered_income
#
#             # SERVICE bo'yicha umumiy to'lanishi kerak bo'lgan to'lov
#             service_due_payment = service_filtered_outcome - service_filtered_income
#
#         else:
#             # Buyurtmalar umumiy soni
#             orders = Order.objects.count()
#
#             # Buyurtmalarning product bo'yicha soni
#             product_orders = Order.objects.filter(
#                 product="PRODUCT"
#             ).count()
#
#             # Buyurtmalarning service bo'yicha soni
#             service_orders = Order.objects.filter(
#                 product="SERVICE"
#             ).count()
#
#             # Barcha buyurtmalarning umumiy narxi
#             orders_sum_price = Order.objects.aggregate(total=Sum("price"))["total"] or 0
#
#             # PRODUCT bo'yicha buyurtmalarning umumiy narxi
#             product_orders_sum_price = Order.objects.filter(
#                 product="PRODUCT"
#             ).aggregate(total=Sum("price"))["total"] or 0
#
#             # SERVICE bo'yicha buyurtmalarning umumiy narxi
#             service_orders_sum_price = Order.objects.filter(
#                 product="SERVICE"
#             ).aggregate(total=Sum("price"))["total"] or 0
#
#             # Umumiy to'lanishi kerak bo'lgan to'lov
#             due_payment = total_outcome - total_income
#
#             # PRODUCT bo'yicha umumiy to'lanishi kerak bo'lgan to'lov
#             product_due_payment = total_product_outcome - total_product_income
#
#             # SERVICE bo'yicha umumiy to'lanishi kerak bo'lgan to'lov
#             service_due_payment = total_service_outcome - total_service_income
#
#             # Umumiy to'lov
#             filtered_income = total_income
#
#             # PRODUCT bo'yicha umumiy to'lov
#             product_filtered_income = total_product_income
#
#             # SERVICE bo'yicha umumiy to'lov
#             service_filtered_income = total_service_income
#
#         customer_debt = total_income - total_outcome  # Customer umumiy qarzi
#         customer_product_debt = total_product_income - total_product_outcome  # customer mahsulot bo'yicha qarzi
#         customer_service_debt = total_service_income - total_service_outcome  # customer xizmat bo'yicha qarzi
#
#         user_debt = total_outcome - total_income
#         user_product_debt = total_product_outcome - total_product_income
#         user_service_debt = total_service_outcome - total_service_income
#
#         return Response(
#             {
#                 # Mijoz qarzi
#                 "customer_debt": customer_debt if customer_debt < 0 else 0,
#                 "customer_product_debt": customer_product_debt if customer_product_debt < 0 else 0,
#                 "customer_service_debt": customer_service_debt if customer_service_debt < 0 else 0,
#
#                 # Admin qarzi
#                 "user_debt": user_debt if user_debt < 0 else 0,
#                 "user_product_debt": user_product_debt if user_product_debt < 0 else 0,
#                 "user_service_debt": user_service_debt if user_service_debt < 0 else 0,
#
#                 # Buyurtmalar soni
#                 "orders_count": orders,
#                 "product_orders_count": product_orders,
#                 "service_orders_count": service_orders,
#
#                 # Umumiy buyurtmalar narxi
#                 "orders_sum_price": orders_sum_price,
#                 "product_orders_sum_price": product_orders_sum_price,
#                 "service_orders_sum_price": service_orders_sum_price,
#
#                 # To'lovlar
#                 "income": filtered_income,
#                 "product_income": product_filtered_income,
#                 "service_income": service_filtered_income,
#
#                 # Kutilayotgan to'lovlar
#                 "due_payment": due_payment if due_payment > 0 else 0,
#                 "product_due_payment": product_due_payment if product_due_payment > 0 else 0,
#                 "service_due_payment": service_due_payment if service_due_payment > 0 else 0,
#             },
#             status=status.HTTP_200_OK,
#         )
