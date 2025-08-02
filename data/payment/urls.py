from django.urls import path
from data.payment.views import *

urlpatterns = [
    path("", PaymentListView.as_view(), name="payment_list"),
    path("debt_splits", DebtSplitsListAPIView.as_view()),
]
