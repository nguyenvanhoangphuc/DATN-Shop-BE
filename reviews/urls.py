from django.urls import path, include
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=False)
router.register(r'review', views.ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]

