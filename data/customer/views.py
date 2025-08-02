from typing import cast
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from data.common.pagination import CustomPagination
from data.customer.serializers import *

from rest_framework.decorators import action

from rest_framework.response import Response


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_serializer_context(self):
        return {"request": self.request}

    @action(detail=True, methods=["get", "post"], url_path="recalculate")
    def recalculate(self, request):

        customer: "Customer" = cast(Customer, self.get_object())

        customer.recalculate_balance()

        return Response(CustomerSerializer(customer).data)
