from django.urls import path, include
from rest_framework import routers

from data.order.views import *

router = routers.DefaultRouter()
router.register("", OrderViewSet)

urlpatterns = router.urls
