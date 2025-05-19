from django.urls import path, include
from . import views

urlpatterns = [
    path('auth/', include('authentication.urls')),
    path('upload/', views.UploadImageView.as_view(), name='upload-image'),
    path('', include('users.urls')),
]
