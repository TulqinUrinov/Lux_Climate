from django.utils.dateparse import parse_date
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from data.bot.permission import IsBotAuthenticated
from data.common.pagination import CustomPagination
from data.order.serializers import *


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [IsBotAuthenticated]
    pagination_class = CustomPagination

    def get_serializer_class(self):

        # Barcha buyurtmalar ro'yxati
        if self.action == "list":
            return OrderListSerializer

        # # 1 ta customerga tegishli barcha buyurtmalar
        # elif self.action == "customer_orders":
        #     return CustomerOrderSerializer

        # faqat 1 buyurtma haqidagi ma'lumotlar
        elif self.action == "retrieve":
            return OrderSerializer

        return OrderCreateUpdateSerializer

    def get_queryset(self):

        queryset = Order.objects.all()

        customer_id = self.request.query_params.get('customer_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        if start_date:
            queryset = queryset.filter(created_at__gte=parse_date(start_date))

        if end_date:
            queryset = queryset.filter(created_at__lte=parse_date(end_date))

        return queryset

    # @action(detail=False, methods=["get"], url_path="by_customer")
    # def customer_orders(self, request):
    #     customer_id = request.query_params.get("customer_id")
    #
    #     if not customer_id:
    #         return Response(
    #             {"error": "customer_id is required"}, status=status.HTTP_400_BAD_REQUEST
    #         )
    #
    #     orders = Order.objects.filter(customer_id=customer_id)
    #
    #     # pagination
    #     page = self.paginate_queryset(orders)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #
    #     serializer = self.get_serializer(orders, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):

        serializer.save(created_by=self.request.admin)
