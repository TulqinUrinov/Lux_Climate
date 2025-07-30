from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from data.common.pagination import CustomPagination
from data.customer.serializers import *


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_serializer_context(self):
        return {'request': self.request}
