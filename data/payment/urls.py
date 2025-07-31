from django.urls import path
from data.payment.views import *

urlpatterns = [
    path('payment_list/', PaymentListView.as_view(), name='payment_list')
]
