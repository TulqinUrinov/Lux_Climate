from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from data.order.models import Order
from data.order.serializers import OrderSerializer, OrderListSerializer
from data.user.permission import UserPermission


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]


class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]
