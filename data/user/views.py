from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer
from ..bot.permission import IsBotAuthenticated
from ..common.pagination import CustomPagination


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_archived=False)
    serializer_class = UserSerializer
    permission_classes = [IsBotAuthenticated]
    pagination_class = CustomPagination

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_archived = True
        instance.save()

        return Response(
            {"detail": "User has been archived"},
            status=status.HTTP_204_NO_CONTENT
        )

    # @action(detail=True, methods=['post'])
    # def restore(self, request, pk=None):
    #     user = self.get_object()
    #     user.is_archived = False
    #     user.save()
    #     return Response({"detail": "User restored successfully."})
