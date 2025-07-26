from django.urls import path, include
from rest_framework import routers

from data.order.views import OrderViewSet

order_router = routers.DefaultRouter()
order_router.register('orders', OrderViewSet)

urlpatterns = [
    path('', include(order_router.urls)),
]
