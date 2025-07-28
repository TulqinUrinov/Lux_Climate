from datetime import date, datetime, time

from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from data.customer.serializers import *
from data.order.models import Order
from data.user.permission import UserPermission


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_class = [IsAuthenticated, UserPermission]


class CustomerOrderAPIView(APIView):
    def get(self, request, customer_id):
        orders = Order.objects.filter(customer_id=customer_id)
        serializer = CustomerOrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerOrderPaymentAPIView(APIView):
    def get(self, request, customer_id):
        payments = Balance.objects.filter(customer_id=customer_id, type='income')
        serializer = CustomerOrderPaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerOrderDebtAPIView(APIView):
    def get(self, request, customer_id):
        debt = Balance.objects.filter(customer_id=customer_id, type='outcome')
        serializer = CustomerOrderDebtSerializer(debt, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerBalanceAPIView(APIView):
    def get(self, request, customer_id):
        income = Balance.objects.filter(customer_id=customer_id, type='income').aggregate(total=Sum('amount'))[
                     'total'] or 0
        outcome = Balance.objects.filter(customer_id=customer_id, type='outcome').aggregate(total=Sum('amount'))[
                      'total'] or 0
        balance = income - outcome
        orders_count = Order.objects.filter(customer_id=customer_id).count()

        return Response(
            {
                'orders_count': orders_count,
                'balance': balance
            },
            status=status.HTTP_200_OK
        )


class CustomerListAPIView(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            today = date.today()
            start_datetime = datetime.combine(today, time.min)
            end_datetime = datetime.combine(today, time.max)

        else:
            start_datetime = datetime.combine(datetime.strptime(start_date, '%Y-%m_%d'), time.min)
            end_datetime = datetime.combine(datetime.strptime(end_date, '%Y-%m_%d'), time.max)

        customers = Customer.objects.all()
        result = []

        for customer in customers:
            income = Balance.objects.filter(customer=customer, type='income',
                                            created_at__range=[start_datetime, end_datetime]
                                            ).aggregate(total=Sum('amount'))['total'] or 0

            outcome = Balance.objects.filter(customer=customer, type='outcome',
                                             created_at__range=[start_datetime, end_datetime]
                                             ).aggregate(total=Sum('amount'))['total'] or 0

            balance = income - outcome

            result.append(
                {
                    'customer': customer.id,
                    'balance': balance
                }
            )

        return Response(result, status=status.HTTP_200_OK)
