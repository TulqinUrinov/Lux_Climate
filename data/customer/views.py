from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from data.customer.models import Customer
from data.customer.serializers import CustomerSerializer
from data.user.permission import UserPermission


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_class = [IsAuthenticated, UserPermission]
