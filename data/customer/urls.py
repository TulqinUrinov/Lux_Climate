from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"", CustomerViewSet, basename="customer")

urlpatterns = [
                  path('list/', CustomerListAPIView.as_view()),
              ] + router.urls
