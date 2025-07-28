from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('orders/<int:customer_id>/', CustomerOrderAPIView.as_view(), name='customer_order'),
    path('payments/<int:customer_id>/', CustomerOrderPaymentAPIView.as_view(), name='customer_payment'),
    path('debt/<int:customer_id>/', CustomerOrderDebtAPIView.as_view(), name='customer_debt'),

    path('balance/<int:customer_id>/', CustomerBalanceAPIView.as_view(), name='customer_balance'),
    path('customers_list/', CustomerListAPIView.as_view(), name='customers_list'),

]
