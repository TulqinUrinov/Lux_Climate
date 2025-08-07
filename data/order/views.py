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
        if self.action == "list":
            return OrderListSerializer

        elif self.action == "customer_orders":
            return CustomerOrderSerializer

        elif self.action == "retrieve":   #, "create", "update", "partial_update"]:
            return OrderSerializer

        return OrderCreateSerializer

    @action(detail=False, methods=["get"], url_path="by_customer")
    def customer_orders(self, request):
        customer_id = request.query_params.get("customer_id")

        if not customer_id:
            return Response(
                {"error": "customer_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        orders = Order.objects.filter(customer_id=customer_id)

        # pagination
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):

        serializer.save(created_by=self.request.admin)
