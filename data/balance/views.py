from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers

from .models import Balance
from .services import mutual_settlements
from .serializers import MutualSettlementSerializer, BalanceSerializer


class BalanceCreateAPIView(CreateAPIView):
    serializer_class = BalanceSerializer
    queryset = Balance.objects.all()

    def perform_create(self, serializer):
        data = self.request.data
        if data.get("type") == "outcome":
            change = -abs(float(data["amount"]))
        elif data.get("type") == "income":
            change = abs(float(data["amount"]))
        else:
            raise serializers.ValidationError({"type": ["Noto‘g‘ri turdagi transaction."]})

        serializer.save(change=change)


class MutualSettlementView(APIView):
    def get(self, request, customer_id):
        settlements = mutual_settlements(
            self,
            customer_id=customer_id,
            last_one=False
        )

        if not settlements:
            return Response({"detail": "Ma'lumot topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MutualSettlementSerializer(settlements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
