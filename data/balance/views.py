from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics

from .models import Balance
from .services import mutual_settlements
from .serializers import MutualSettlementSerializer, BalanceSerializer


# class BalanceCreateAPIView(APIView):
#     def post(self, request):
#         serializer = BalanceSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BalanceCreateAPIView(generics.CreateAPIView):
    queryset = Balance.objects.all()
    serializer_class = BalanceSerializer


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
