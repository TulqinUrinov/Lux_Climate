from rest_framework.permissions import BasePermission

class IsBotAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(
            getattr(request, "bot_user", None)
            and (getattr(request, "admin", None) or getattr(request, "customer", None))
        )