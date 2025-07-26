from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from data.order.models import Order, OrderFile
from data.order.serializers import OrderSerializer, OrderFileSerializer
from data.user.permission import UserPermission


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, UserPermission]


class OrderFileViewSet(viewsets.ModelViewSet):
    queryset = OrderFile.objects.all()
    serializer_class = OrderFileSerializer
    permission_classes = [IsAuthenticated, UserPermission]
