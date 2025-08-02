from django.urls import path
from data.payment.views import *

urlpatterns = [path("", PaymentListView.as_view(), name="payment_list")]
