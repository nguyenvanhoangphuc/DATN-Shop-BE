"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import Http404

schema_view = get_schema_view(
   openapi.Info(
      title="Website API",
      default_version='v1',
      description="API cho hệ thống website thương mại điện tử",
      terms_of_service="https://www.example.com/terms/",
      contact=openapi.Contact(email="phucnvh2310@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   authentication_classes= (),
)

def not_found_view(request):
    raise Http404("Đường dẫn không đúng hoặc bị thừa dấu \ cuối cùng.")

urlpatterns = [
    path('admin', admin.site.urls),
    path('api/', include('app.urls')),  # app chứa các API như login, register...
    
    # Swagger routes
    path('swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # Not fault page
    path('/:pk', not_found_view),
]

