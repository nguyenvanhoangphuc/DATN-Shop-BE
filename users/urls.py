from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')

urlpatterns = [
    path('user/search-and/', views.UserSearchView.as_view(), name='user-search-and'),
    path('user/search-or/', views.UserSearchViewOR.as_view(), name='user-search-or'),
    path('', include(router.urls)),
]

