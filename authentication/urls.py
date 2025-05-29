from django.urls import path, include
from .views import *

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', Logout.as_view(), name='logout'),
    path('validate', Validate.as_view(), name='validate'),
    path('refresh_token', RefreshToken.as_view(), name='refresh_token'),
]