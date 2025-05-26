from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'category', views.CategoryViewSet, basename='category')
router.register(r'material', views.MaterialViewSet, basename='material')
router.register(r'brand', views.BrandViewSet, basename='brand')
router.register(r'product', views.ProductViewSet, basename='product')
router.register(r'sub-product', views.SubProductViewSet, basename='sub-product')
router.register(r'product-sub-product', views.ProductSubProductViewSet, basename='product-sub-product')

urlpatterns = [
    path('product/search-and/', views.ProductSearchView.as_view(), name='product-search-and'),
    path('product/search-or/', views.ProductSearchViewOR.as_view(), name='product-search-or'),
    path('', include(router.urls)),
]

