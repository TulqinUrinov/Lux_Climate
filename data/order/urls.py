from django.urls import path, include
from rest_framework import routers

from data.order.views import OrderViewSet, OrderFileViewSet

order_router = routers.DefaultRouter()
order_router.register('orders', OrderViewSet)
file_router = routers.DefaultRouter()
file_router.register('files', OrderFileViewSet)

urlpatterns = [
    path('', include(order_router.urls)),
    path('', include(file_router.urls)),
]