from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from data.order.models import Order
from data.order.serializers import OrderSerializer
from data.user.permission import UserPermission


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]



