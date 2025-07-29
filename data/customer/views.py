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

        start_datetime = None
        end_datetime = None

        try:
            if start_date:
                start_datetime = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d'), time.min)
            if end_date:
                end_datetime = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d'), time.max)
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

        customers = Customer.objects.all()
        result = []

        if start_date and end_date:

            for customer in customers:
                print(customer.id)
                income = Balance.objects.filter(customer=customer, type='income',
                                                created_at__range=[start_datetime, end_datetime]
                                                ).aggregate(total=Sum('amount'))['total'] or 0

                outcome = Balance.objects.filter(customer=customer, type='outcome',
                                                 created_at__range=[start_datetime, end_datetime]
                                                 ).aggregate(total=Sum('amount'))['total'] or 0

        else:
            for customer in customers:
                income = Balance.objects.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
                outcome = Balance.objects.filter(type='outcome').aggregate(total=Sum('amount'))['total'] or 0

        balance = income - outcome

        result.append(
            {
                'customer': customer.id,
                'balance': balance
            }
        )

        return Response(result, status=status.HTTP_200_OK)
