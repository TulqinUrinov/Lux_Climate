from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'customer', CustomerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('customer/status/<int:customer_id>/', CustomerBalanceAPIView.as_view(), name='customer_balance'),
    path('customer/status/customers_list/', CustomerListAPIView.as_view(), name='customers_list'),

]
