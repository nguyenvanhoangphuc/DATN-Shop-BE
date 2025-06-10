from django.urls import path, include
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=False)
router.register(r'paymentMethod', views.PaymentMethodViewSet, basename='paymentMethod')
router.register(r'payment', views.PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]

