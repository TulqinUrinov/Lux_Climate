from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from data.common.pagination import CustomPagination
from data.order.serializers import *


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer

        elif self.action == 'customer_orders':
            return CustomerOrderSerializer

        elif self.action == 'customer_debts':
            return CustomerOrderDebtSerializer

        return OrderSerializer

    @action(detail=False, methods=['get'], url_path='by-customer')
    def customer_orders(self, request):
        customer_id = request.query_params.get('customer_id')

        if not customer_id:
            return Response({'error': 'customer_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        orders = Order.objects.filter(customer_id=customer_id)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='debt-by-customer')
    def customer_debts(self, request):
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response({'error': 'customer_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        debts = Balance.objects.filter(customer_id=customer_id, type='outcome')
        serializer = self.get_serializer(debts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
