from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer
from ..bot.permission import IsBotAuthenticated
from ..common.pagination import CustomPagination


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsBotAuthenticated]
    pagination_class = CustomPagination
