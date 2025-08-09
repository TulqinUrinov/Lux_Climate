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


class BalanceCreateAPIView(CreateAPIView):
    serializer_class = BalanceSerializer
    queryset = Balance.objects.all()
    permission_classes = [IsBotAuthenticated]

    def perform_create(self, serializer):
        data = self.request.data
        if data.get("type") == "OUTCOME":
            change = -abs(float(data["amount"]))
        elif data.get("type") == "INCOME":
            change = abs(float(data["amount"]))
        else:
            raise serializers.ValidationError(
                {"type": ["Noto‘g‘ri turdagi transaction."]}
            )

        serializer.save(change=change)


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

        # Umumiy (filternatsiya qilinmagan) income va outcome
        total_income = (
                Balance.objects.filter(type="INCOME").aggregate(
                    total=Sum("amount"))["total"] or 0
        )
        print(total_income)

        total_outcome = (
                Balance.objects.filter(type="OUTCOME").aggregate(
                    total=Sum("amount"))["total"] or 0
        )
        print(total_outcome)

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
            orders = Order.objects.filter(
                created_at__range=[start_datetime, end_datetime]
            ).count()

            orders_sum_price = (
                    Order.objects.filter(
                        created_at__range=[start_datetime, end_datetime]
                    ).aggregate(total=Sum("price"))["total"]
                    or 0
            )

            # Sana bo‘yicha filternatsiya qilamiz
            filtered_income = (
                    Balance.objects.filter(
                        type="INCOME", created_at__range=[start_datetime, end_datetime]
                    ).aggregate(total=Sum("amount"))["total"]
                    or 0
            )

            filtered_outcome = (
                    Balance.objects.filter(
                        type="OUTCOME", created_at__range=[start_datetime, end_datetime]
                    ).aggregate(total=Sum("amount"))["total"]
                    or 0
            )

            due_payment = filtered_outcome - filtered_income

        else:
            orders = Order.objects.count()
            orders_sum_price = Order.objects.aggregate(total=Sum("price"))["total"] or 0

            due_payment = total_outcome - total_income

            # Agar sana yo'q bo‘lsa, income ham umumiy bo'ladi
            filtered_income = total_income

        customer_debt = total_income - total_outcome
        user_debt = total_outcome - total_income

        return Response(
            {
                "customer_debt": customer_debt,
                "user_debt": user_debt if user_debt < 0 else 0,
                "orders_count": orders,
                "orders_sum_price": orders_sum_price,
                "income": filtered_income,
                "due_payment": due_payment,
            },
            status=status.HTTP_200_OK,
        )
