from django.urls import path

from .report import BalanceReportExportView
from .views import MutualSettlementView, BalanceCreateAPIView, BalanceStatusView

urlpatterns = [
    path('get/<int:customer_id>/', MutualSettlementView.as_view(), name='balance_get'),
    path('create/', BalanceCreateAPIView.as_view(), name='balance_create'),
    path('balance_status/', BalanceStatusView.as_view(), name='balance_status'),
    path('balance/export/', BalanceReportExportView.as_view(), name='balance-export'),
]
