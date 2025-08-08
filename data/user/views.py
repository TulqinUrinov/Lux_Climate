from rest_framework import viewsets, status, filters
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer
from ..bot.permission import IsBotAuthenticated
from ..common.pagination import CustomPagination


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_archived=False).order_by("-created_at")
    serializer_class = UserSerializer
    permission_classes = [IsBotAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["full_name", "phone_number"]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_archived = True
        instance.save()

        return Response(
            {"detail": "User has been archived"},
            status=status.HTTP_204_NO_CONTENT
        )
