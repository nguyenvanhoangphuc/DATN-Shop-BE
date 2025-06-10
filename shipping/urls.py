from django.urls import path, include
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=False)
router.register(r'shipping', views.ShippingViewSet, basename='shipping')

urlpatterns = [
    path('', include(router.urls)),
]

