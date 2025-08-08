from typing import cast
from rest_framework import viewsets, status, filters, generics

from data.bot.permission import IsBotAuthenticated
from data.common.pagination import CustomPagination
from data.customer.serializers import *

from rest_framework.decorators import action

from rest_framework.response import Response


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.filter(is_archived=False).order_by("-created_at")
    serializer_class = CustomerSerializer
    permission_classes = [IsBotAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["full_name", "phone_number"]

    def get_serializer_context(self):
        return {"request": self.request}

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_archived = True
        instance.save()
        return Response(
            {"detail": "Customer has been archived"},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=["get", "post"], url_path="recalculate")
    def recalculate(self, request, pk):
        customer: "Customer" = cast(Customer, self.get_object())

        customer.recalculate_balance()

        return Response(CustomerSerializer(customer).data)


# Paginationsiz
class CustomerListAPIView(generics.ListAPIView):
    queryset = Customer.objects.filter(is_archived=False).order_by("-created_at")
    serializer_class = CustomerSerializer
    permission_classes = [IsBotAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["full_name", "phone_number"]
