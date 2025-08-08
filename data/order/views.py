from django.utils.dateparse import parse_date
from rest_framework import viewsets

from data.bot.permission import IsBotAuthenticated
from data.common.pagination import CustomPagination
from data.order.serializers import *


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    permission_classes = [IsBotAuthenticated]
    pagination_class = CustomPagination

    def get_serializer_class(self):

        # Barcha buyurtmalar ro'yxati
        if self.action == "list":
            return OrderListSerializer

        # faqat 1 buyurtma haqidagi ma'lumotlar
        elif self.action == "retrieve":
            return OrderSerializer

        return OrderCreateUpdateSerializer

    def get_queryset(self):

        queryset = Order.objects.all().order_by('-created_at')

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

    def perform_create(self, serializer):

        serializer.save(created_by=self.request.admin)
