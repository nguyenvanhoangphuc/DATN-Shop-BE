from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'wishList', views.WishListViewSet, basename='wishList')

urlpatterns = [
    path('', include(router.urls)),
]

