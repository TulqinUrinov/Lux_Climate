from django.urls import path
from .views import MutualSettlementView, BalanceCreateAPIView, PaymentListView, BalanceStatusView

urlpatterns = [
    path('get/<int:customer_id>/', MutualSettlementView.as_view(), name='balance_get'),
    path('create/', BalanceCreateAPIView.as_view(), name='balance_create'),
    path('payment_list/', PaymentListView.as_view(), name ='payment_list'),
    path('balance_status/', BalanceStatusView.as_view(), name='balance_status'),
]
