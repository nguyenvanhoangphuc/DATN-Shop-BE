from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')

urlpatterns = [
    # path('hello/', views.HelloWorldView.as_view(), name='hello-world'),
    path('', include(router.urls)),
]

