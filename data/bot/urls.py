from django.urls import path
from .views import *

urlpatterns = [
    path('bot/token', JWTtokenGenerator.as_view(), name='auth'),
    path('bot/refresh', JWTtokenRefresh.as_view(), name='refresh'),
    path('me', Me.as_view(), name='me'),
]