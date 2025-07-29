from django.urls import path

from .report import BalanceReportExportView
from .views import MutualSettlementView, BalanceCreateAPIView, BalanceStatusView

urlpatterns = [
    path('balance/get/<int:customer_id>/', MutualSettlementView.as_view(), name='balance_get'),
    path('balance/create/', BalanceCreateAPIView.as_view(), name='balance_create'),
    path('balance/status/', BalanceStatusView.as_view(), name='balance_status'),
    path('balance/export/', BalanceReportExportView.as_view(), name='balance_export'),
]
