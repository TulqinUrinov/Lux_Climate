from django.urls import path
from data.payment.views import *

urlpatterns = [
    path("", PaymentListCreateView.as_view(), name="payment_list"),
    path("update/<int:pk>/", PaymentUpdateView.as_view(), name="payment-update"),
    path("debt_splits/", DebtSplitsListAPIView.as_view()),
]
