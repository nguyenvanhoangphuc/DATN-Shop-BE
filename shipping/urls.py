from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'shipping', views.ShippingViewSet, basename='shipping')

urlpatterns = [
    path('', include(router.urls)),
]

