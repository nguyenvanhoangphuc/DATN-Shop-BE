from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'coupon', views.CouponViewSet, basename='coupon')

urlpatterns = [
    path('', include(router.urls)),
]

