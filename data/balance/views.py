from datetime import date, datetime, time
from django.db.models import Sum
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .services import mutual_settlements
from .serializers import *
from ..order.models import Order
from ..payment.models import InstallmentPayment


class BalanceCreateAPIView(CreateAPIView):
    serializer_class = BalanceSerializer
    queryset = Balance.objects.all()

    def perform_create(self, serializer):
        data = self.request.data
        if data.get("type") == "outcome":
            change = -abs(float(data["amount"]))
        elif data.get("type") == "income":
            change = abs(float(data["amount"]))
        else:
            raise serializers.ValidationError({"type": ["Noto‘g‘ri turdagi transaction."]})

        serializer.save(change=change)


class MutualSettlementView(APIView):
    def get(self, request, customer_id):
        settlements = mutual_settlements(
            self,
            customer_id=customer_id,
            last_one=False
        )

        if not settlements:
            return Response({"detail": "Ma'lumot topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MutualSettlementSerializer(settlements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BalanceStatusView(APIView):

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        start_datetime = None
        end_datetime = None

        try:
            if start_date:
                start_datetime = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d'), time.min)
            if end_date:
                end_datetime = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d'), time.max)
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

        result = []

        if start_date and end_date:
            income = Balance.objects.filter(
                type='income',
                created_at__range=[start_datetime, end_datetime]
            ).aggregate(total=Sum('amount'))['total'] or 0

            outcome = Balance.objects.filter(
                type='outcome',
                created_at__range=[start_datetime, end_datetime]
            ).aggregate(total=Sum('amount'))['total'] or 0

            orders = Order.objects.filter(
                created_at__range=[start_datetime, end_datetime]
            ).count()

            orders_sum_price = Order.objects.filter(
                created_at__range=[start_datetime, end_datetime]
            ).aggregate(total=Sum('price'))['total'] or 0

            due_payment = InstallmentPayment.objects.filter(
                payment_date__gt=end_datetime
            ).aggregate(total=Sum('amount'))['total'] or 0
        else:
            # Agar start_date yoki end_date berilmasa, umumiy statistika
            income = Balance.objects.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
            outcome = Balance.objects.filter(type='outcome').aggregate(total=Sum('amount'))['total'] or 0
            orders = Order.objects.count()
            orders_sum_price = Order.objects.aggregate(total=Sum('price'))['total'] or 0
            due_payment = InstallmentPayment.objects.aggregate(total=Sum('amount'))['total'] or 0

        customer_debt = income - outcome
        user_debt = outcome - income

        result.append({
            'customer_debt': customer_debt,
            'user_debt': user_debt if user_debt < 0 else 0,
            'orders_count': orders,
            'orders_sum_price': orders_sum_price,
            'income': income,
            'due_payment': due_payment,
        })

        return Response(result, status=status.HTTP_200_OK)
