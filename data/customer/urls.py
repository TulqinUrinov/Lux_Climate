from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"", CustomerViewSet, basename="customer")

urlpatterns = [
    path('', include(router.urls)),
    path('list/', CustomerListAPIView.as_view())
]
