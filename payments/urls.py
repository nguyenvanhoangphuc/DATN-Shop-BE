from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'paymentMethod', views.PaymentMethodViewSet, basename='paymentMethod')
router.register(r'payment', views.PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]

