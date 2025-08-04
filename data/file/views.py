from rest_framework import viewsets

from data.bot.permission import IsBotAuthenticated
from data.common.pagination import CustomPagination
from data.file.serializers import FileSerializer

from data.file.models import File


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsBotAuthenticated]
    pagination_class = CustomPagination
