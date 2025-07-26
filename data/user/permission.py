from rest_framework.permissions import BasePermission

from data.user.models import User


class UserPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and isinstance(getattr(request.user, 'user', None), User)
