from django.urls import path
from .views import MutualSettlementView, BalanceCreateAPIView

urlpatterns = [
    path('get/<int:customer_id>/', MutualSettlementView.as_view(), name='balance_get'),
    path('create/', BalanceCreateAPIView.as_view(), name='balance_create')
]
