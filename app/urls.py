from django.urls import path, include
from . import views

urlpatterns = [
    path('auth/', include('authentication.urls')),
    path('upload/', views.UploadImageView.as_view(), name='upload-image'),
    path('', include('users.urls')),
    path('', include('coupons.urls')),
    path('', include('products.urls')),
    path('', include('carts.urls')),
    path('', include('orders.urls')),
    path('', include('payments.urls')),
    path('', include('reviews.urls')),
    path('', include('shipping.urls')),
    path('', include('wishlist.urls')),
]
