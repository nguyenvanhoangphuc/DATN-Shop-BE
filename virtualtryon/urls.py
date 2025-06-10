from django.urls import path
from .views import virtual_tryon

urlpatterns = [
    path("virtualtryon", virtual_tryon, name="virtualtryon"),
]
