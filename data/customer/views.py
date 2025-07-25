from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from data.customer.models import Customer
from data.customer.serializers import CustomerSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    pagination_class = IsAuthenticated
