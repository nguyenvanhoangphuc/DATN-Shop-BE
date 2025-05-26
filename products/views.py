from django.db.models import Q
from rest_framework.response import Response
from rest_framework import viewsets, generics, status
from rest_framework.exceptions import ValidationError
from products.serializers import ProductSerializer, ProductSerializerOutput, ProductUpdateSerializer, IdsProductSerializer, CategorySerializer, CategorySerializerOutput, CategoryUpdateSerializer, IdsCategorySerializer, MaterialSerializer, MaterialSerializerOutput, MaterialUpdateSerializer, IdsMaterialSerializer, BrandSerializer, BrandSerializerOutput, BrandUpdateSerializer, IdsBrandSerializer, SubProductSerializer, SubProductSerializerOutput, SubProductUpdateSerializer, IdsSubProductSerializer, ProductSubProductSerializer, ProductSubProductSerializerOutput, ProductSubProductUpdateSerializer, IdsProductSubProductSerializer
from app.serializers import ResponseSerializer
from products.models import Category, Material, Brand, Product, StatusEnum, SubProduct, ProductSubProduct
import requests
from rest_framework.decorators import action
from authentication.permissions import IsCustomerPermission, IsAdminPermission, IsAuthenticatedPermission
from drf_yasg.utils import swagger_auto_schema

## generic
def soft_delete_subproduct(sub_product):
    if sub_product.status_enum != StatusEnum.DELETED.value:
        sub_product.status_enum = StatusEnum.DELETED.value
        sub_product.save()
        print(f"Soft deleted SubProduct: {sub_product}")

def soft_delete_product(product):
    if product.status_enum != StatusEnum.DELETED.value:
        product.status_enum = StatusEnum.DELETED.value
        product.save()
        print(f"Soft deleted Product: {product.name}")

    # Soft delete all subproducts through ProductSubProduct
    product_subproducts = product.sub_products.select_related('sub_product')
    for link in product_subproducts:
        soft_delete_subproduct(link.sub_product)

    # Also optionally: soft delete the ProductSubProduct link itself
    for link in product_subproducts:
        if link.status_enum != StatusEnum.DELETED.value:
            link.status_enum = StatusEnum.DELETED.value
            link.save()

def recursive_soft_delete(category):
    if category.status_enum != StatusEnum.DELETED.value:
        category.status_enum = StatusEnum.DELETED.value
        category.save()
        print(f"Soft deleted Category: {category.name}")

    # Soft delete all products under this category
    for product in category.products.all():
        soft_delete_product(product)

    # Continue with subcategories
    for subcategory in category.subcategories.all():
        recursive_soft_delete(subcategory)

## Category
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        if getattr(self, 'action', None) in ['list', 'retrieval']:
            return []
        return super().get_authenticators()


    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['list', 'retrieve']:
            return []
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'soft_delete', 'multiple_delete', 'multiple_destroy']:
            return [IsAdminPermission()]  
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return CategoryUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return CategorySerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsCategorySerializer
        return CategorySerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in Category._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("category list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CategorySerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CategorySerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("category retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=CategoryUpdateSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("category create")
        data = request.data.copy()
        parent_id = request.data.get('parent_id', None)
        print("parent_id", parent_id)
        if parent_id!=None: 
            try:
                parent = Category.objects.get(id=parent_id)
                data['parent'] = parent.id
                print("vao day")
            except Category.DoesNotExist:
                return Response({'detail': 'Category not found'}, status=status.HTTP_403_FORBIDDEN) 
        category = CategorySerializer(data=data)
        if category.is_valid():
            category.save()
        else:
            return Response(
                {"detail": "Category is invalid",  "errors": category.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"category": category.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        parent_id = request.data.get('parent_id', None)
        print("parent_id", parent_id)
        if parent_id!=None: 
            try:
                parent = Category.objects.get(id=parent_id)
                data['parent'] = parent.id
                print("vao day")
            except Category.DoesNotExist:
                return Response({'detail': 'Category not found'}, status=status.HTTP_403_FORBIDDEN) 
        
        category = CategorySerializer(instance, data=data, partial=partial)
        category.is_valid(raise_exception=True)
        category.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("category partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()

        parent_id = request.data.get('parent_id', None)
        print("parent_id", parent_id)
        if parent_id!=None: 
            try:
                parent = Category.objects.get(id=parent_id)
                data['parent'] = parent.id
                print("vao day")
            except Category.DoesNotExist:
                return Response({'detail': 'Category not found'}, status=status.HTTP_403_FORBIDDEN) 
            
        category = CategorySerializer(instance, data=data, partial=partial)
        category.is_valid(raise_exception=True)
        category.save()

        return Response(category.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("Category destroy")
        pk = kwargs.get('pk')
        
        try:
            instance = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({'detail': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        
        instance.delete()
        return Response({'detail': 'Category deleted successfully'}, status=status.HTTP_200_OK)


    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("Category soft_delete")
        # Lấy category cần xóa
        instance = self.get_object()
        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'Category already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Bắt đầu xoá mềm từ category hiện tại
        recursive_soft_delete(instance)
        return Response({'detail': 'Category and its subcategories soft deleted successfully'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(responses={200: ResponseSerializer})
    def multiple_delete(self, request):
        print("Category multiple_delete")
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response({'detail': 'No category IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

        categories = Category.objects.filter(id__in=ids)

        if not categories.exists():
            return Response({'detail': 'No categories found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)

        for category in categories:
            recursive_soft_delete(category)

        return Response({'detail': 'Categories and their subcategories soft deleted successfully'}, status=status.HTTP_200_OK)
        
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(responses={200: ResponseSerializer})
    def multiple_destroy(self, request):
        print("Category multiple_destroy")
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response({'detail': 'No category IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

        categories = Category.objects.filter(id__in=ids)

        if not categories.exists():
            return Response({'detail': 'No categories found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)

        for category in categories:
            category.delete()
            print(f"Deleted: {category.name}")

        return Response({'detail': 'Categories deleted successfully'}, status=status.HTTP_200_OK)


## Material
class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all().order_by('id')
    serializer_class = MaterialSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        if getattr(self, 'action', None) in ['list', 'retrieval']:
            return []
        return super().get_authenticators()


    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['list', 'retrieve']:
            return []
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'soft_delete', 'multiple_delete', 'multiple_destroy']:
            return [IsAdminPermission()]  
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return MaterialUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return MaterialSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsMaterialSerializer
        return MaterialSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in Material._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("material list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MaterialSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MaterialSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("material retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=MaterialSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("material create")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        material = MaterialSerializer(instance, data=data, partial=partial)
        material.is_valid(raise_exception=True)
        material.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("material partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()
        
        material = MaterialSerializer(instance, data=data, partial=partial)
        material.is_valid(raise_exception=True)
        material.save()

        return Response(material.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("material destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = Material.objects.get(id=pk)
        except Material.DoesNotExist:
            return Response({'detail': 'Material not found'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response({'message': 'Material deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
    responses={200: ResponseSerializer}
)
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("Material soft_delete")
        instance = self.get_object()

        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'Material already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)

        # Soft delete all products that use this material
        related_products = instance.products.all()
        for product in related_products:
            soft_delete_product(product)

        # Soft delete the material itself
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()

        return Response({'detail': 'Material and its related products soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(responses={200: ResponseSerializer})
    def multiple_delete(self, request):
        print("Material multiple_delete")
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response({'message': 'No material IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

        materials = Material.objects.filter(id__in=ids)

        if not materials.exists():
            return Response({'message': 'No materials found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)

        for material in materials:
            # Soft delete related products first
            related_products = material.products.all()
            for product in related_products:
                soft_delete_product(product)
            
            # Then soft delete the material
            if material.status_enum != StatusEnum.DELETED.value:
                material.status_enum = StatusEnum.DELETED.value
                material.save()
                print(f"Soft deleted material: {material.name}")

        return Response({'message': 'Materials and their related products soft deleted successfully'}, status=status.HTTP_200_OK)

    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('material multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No material IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        materials = Material.objects.filter(id__in=ids) 
        if not materials.exists():
            return Response({'message': 'No materials found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        for material in materials:
            material.delete()
        return Response({'message': 'Materials destroy successfully'}, status=status.HTTP_200_OK)



## Brand
class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all().order_by('id')
    serializer_class = BrandSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        if getattr(self, 'action', None) in ['list', 'retrieval']:
            return []
        return super().get_authenticators()

    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['list', 'retrieve']:
            return []
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'soft_delete', 'multiple_delete', 'multiple_destroy']:
            return [IsAdminPermission()]  
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return BrandUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return BrandSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsBrandSerializer
        return BrandSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in Brand._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("brand list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = BrandSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = BrandSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("brand retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=BrandSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("brand create")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        brand = BrandSerializer(instance, data=data, partial=partial)
        brand.is_valid(raise_exception=True)
        brand.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("brand partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()
        
        brand = BrandSerializer(instance, data=data, partial=partial)
        brand.is_valid(raise_exception=True)
        brand.save()

        return Response(brand.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("brand destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = Brand.objects.get(id=pk)
        except Brand.DoesNotExist:
            return Response({'detail': 'Brand not found'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response({'message': 'Brand deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(responses={200: ResponseSerializer})
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("brand soft_delete")
        instance = self.get_object()
        
        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'Brand already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)

        # Soft delete all related products
        related_products = instance.products.all()
        for product in related_products:
            soft_delete_product(product)

        # Then soft delete the brand
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()
        
        return Response({'detail': 'Brand and its related products soft deleted successfully'}, status=status.HTTP_200_OK)


    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(responses={200: ResponseSerializer})
    def multiple_delete(self, request):
        print("brand multiple_delete")
        ids = request.data.get('ids', [])

        if not ids:
            return Response({'message': 'No brand IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

        brands = Brand.objects.filter(id__in=ids)

        if not brands.exists():
            return Response({'message': 'No brands found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)

        for brand in brands:
            # Soft delete related products
            related_products = brand.products.all()
            for product in related_products:
                soft_delete_product(product)

            # Soft delete the brand itself
            if brand.status_enum != StatusEnum.DELETED.value:
                brand.status_enum = StatusEnum.DELETED.value
                brand.save()
                print(f"Soft deleted brand: {brand.name}")

        return Response({'message': 'Brands and their related products soft deleted successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('brand multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No brand IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        brands = Brand.objects.filter(id__in=ids) 
        if not brands.exists():
            return Response({'message': 'No brands found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        for brand in brands:
            brand.delete()
        return Response({'message': 'Brands destroy successfully'}, status=status.HTTP_200_OK)


## Product
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        if getattr(self, 'action', None) in ['list', 'retrieval']:
            return []
        return super().get_authenticators()


    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['list', 'retrieve']:
            return []
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'soft_delete', 'multiple_delete', 'multiple_destroy']:
            return [IsAdminPermission()]  
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ProductUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return ProductSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsProductSerializer
        return ProductSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in Product._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("product list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("product retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=ProductUpdateSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("product create")
        data = request.data.copy()

        # Nếu có file image thì xử lý upload
        image_file = request.FILES.get('image')
        if image_file:
            try:
                upload_url = request.build_absolute_uri('/api/upload/')
                upload_response = requests.post(
                    upload_url,
                    files={'image': image_file}
                )
                if upload_response.status_code == 200 or upload_response.status_code == 201:
                    image_url = upload_response.json().get('image_url')
                    if image_url:
                        data['image_url'] = image_url
                    else:
                        return Response({'error': 'Upload thành công nhưng không nhận được URL.'}, status=500)
                else:
                    return Response({'error': 'Lỗi khi upload ảnh.'}, status=upload_response.status_code)
            except Exception as e:
                return Response({'error': f'Lỗi upload ảnh: {str(e)}'}, status=500)

        product = ProductSerializer(data=data)
        if product.is_valid():
            product.save()
        else:
            return Response(
                {"detail": "Product is invalid",  "errors": product.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"product": product.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        # Nếu có file image thì xử lý upload
        image_file = request.FILES.get('image')
        if image_file:
            try:
                upload_url = request.build_absolute_uri('/api/upload/')
                upload_response = requests.post(
                    upload_url,
                    files={'image': image_file}
                )
                if upload_response.status_code == 200 or upload_response.status_code == 201:
                    image_url = upload_response.json().get('image_url')
                    if image_url:
                        data['image_url'] = image_url
                    else:
                        return Response({'error': 'Upload thành công nhưng không nhận được URL.'}, status=500)
                else:
                    return Response({'error': 'Lỗi khi upload ảnh.'}, status=upload_response.status_code)
            except Exception as e:
                return Response({'error': f'Lỗi upload ảnh: {str(e)}'}, status=500)

        product = ProductSerializer(instance, data=data, partial=partial)
        product.is_valid(raise_exception=True)
        product.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("product partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()
        # Nếu có file image thì xử lý upload
        image_file = request.FILES.get('image')
        if image_file:
            try:
                upload_url = request.build_absolute_uri('/api/upload/')
                upload_response = requests.post(
                    upload_url,
                    files={'image': image_file}
                )
                if upload_response.status_code == 200 or upload_response.status_code == 201:
                    image_url = upload_response.json().get('image_url')
                    if image_url:
                        data['image_url'] = image_url
                    else:
                        return Response({'error': 'Upload thành công nhưng không nhận được URL.'}, status=500)
                else:
                    return Response({'error': 'Lỗi khi upload ảnh.'}, status=upload_response.status_code)
            except Exception as e:
                return Response({'error': f'Lỗi upload ảnh: {str(e)}'}, status=500)

        product = ProductSerializer(instance, data=data, partial=partial)
        product.is_valid(raise_exception=True)
        product.save()

        return Response(product.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("product destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response({'message': 'Product deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("product soft_delete")
        product = self.get_object()

        deleted = soft_delete_product(product)
        if not deleted:
            return Response({'detail': 'Product already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Product soft deleted successfully'}, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=False, methods=['post'], url_path='multiple-delete')
    def multiple_delete(self, request):
        print("product multiple_delete")
        ids = request.data.get('ids', [])

        if not ids or not isinstance(ids, list):
            return Response({'message': 'No valid product IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

        products = Product.objects.filter(id__in=ids)
        if not products.exists():
            return Response({'message': 'No products found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)

        deleted_count = 0
        for product in products:
            if soft_delete_product(product):
                deleted_count += 1

        if deleted_count == 0:
            return Response({'message': 'All products were already soft deleted.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'message': f'Soft deleted {deleted_count} product(s) successfully.'
        }, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('product multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No product IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        products = Product.objects.filter(id__in=ids) 
        if not products.exists():
            return Response({'message': 'No products found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        for product in products:
            product.delete()
        return Response({'message': 'Products destroy successfully'}, status=status.HTTP_200_OK)



class ProductSearchView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = []
    
    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        description = self.request.query_params.get('description', None)
        detail_description = self.request.query_params.get('detail_description', None)
        category = self.request.query_params.get('category', None)
        brand = self.request.query_params.get('brand', None)
        material = self.request.query_params.get('material', None)
        
        type_search_name = self.request.query_params.get('type_search_name', None)
        type_search_description = self.request.query_params.get('type_search_description', None)
        type_search_detail_description = self.request.query_params.get('type_search_detail_description', None)
        type_search_category = self.request.query_params.get('type_search_category', None)
        type_search_brand = self.request.query_params.get('type_search_brand', None)
        type_search_material = self.request.query_params.get('type_search_material', None)
                
        queryset = Product.objects.all().order_by('id')
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value)
        
        
        if name:
            if type_search_name == 'exact':
                queryset = queryset.filter(name=name)
            elif type_search_name == 'contains':
                queryset = queryset.filter(name__icontains=name)
            elif type_search_name == 'startswith':
                queryset = queryset.filter(name__istartswith=name)
            elif type_search_name == 'endswith':
                queryset = queryset.filter(name__iendswith=name)
            else:
                raise ValidationError("Require name type search in ['exact', 'contains', 'startswith', 'endswith]")
        if description:
            if type_search_description == 'exact':
                queryset = queryset.filter(description=description)
            elif type_search_description == 'contains':
                queryset = queryset.filter(description__icontains=description)
            elif type_search_description == 'startswith':
                queryset = queryset.filter(description__istartswith=description)
            elif type_search_description == 'endswith':
                queryset = queryset.filter(description__iendswith=description)
            else:
                raise ValidationError("Require description type search in ['exact', 'contains', 'startswith', 'endswith]")
        if detail_description and type_search_detail_description:
            if type_search_detail_description == 'exact':
                queryset = queryset.filter(detail_description=detail_description)
            elif type_search_detail_description == 'contains':
                queryset = queryset.filter(detail_description__icontains=detail_description)
            elif type_search_detail_description == 'startswith':
                queryset = queryset.filter(detail_description__istartswith=detail_description)
            elif type_search_detail_description == 'endswith':
                queryset = queryset.filter(detail_description__iendswith=detail_description)
            else:
                raise ValidationError("Require detail_description type search in ['exact', 'contains', 'startswith', 'endswith]")
        if category and type_search_category:
            if type_search_category == 'exact':
                queryset = queryset.filter(category=category)
            elif type_search_category == 'contains':
                queryset = queryset.filter(category__icontains=category)
            elif type_search_category == 'startswith':
                queryset = queryset.filter(category__istartswith=category)
            elif type_search_category == 'endswith':
                queryset = queryset.filter(category__iendswith=category)
            else:
                raise ValidationError("Require category type search in ['exact', 'contains', 'startswith', 'endswith]")
        if brand:
            if type_search_brand == 'exact':
                queryset = queryset.filter(brand=brand)
            elif type_search_brand == 'contains':
                queryset = queryset.filter(brand__icontains=brand)
            elif type_search_brand == 'startswith':
                queryset = queryset.filter(brand__istartswith=brand)
            elif type_search_brand == 'endswith':
                queryset = queryset.filter(brand__iendswith=brand)
            else:
                raise ValidationError("Require brand type search in ['exact', 'contains', 'startswith', 'endswith]")
        if material:
            if type_search_material == 'exact':
                queryset = queryset.filter(material=material)
            elif type_search_material == 'contains':
                queryset = queryset.filter(material__icontains=material)
            elif type_search_material == 'startswith':
                queryset = queryset.filter(material__istartswith=material)
            elif type_search_material == 'endswith':
                queryset = queryset.filter(material__iendswith=material)
            else:
                raise ValidationError("Require material type search in ['exact', 'contains', 'startswith', 'endswith]")
        
        return queryset
    
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class ProductSearchViewOR(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = []
    
    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        description = self.request.query_params.get('description', None)
        detail_description = self.request.query_params.get('detail_description', None)
        category = self.request.query_params.get('category', None)
        brand = self.request.query_params.get('brand', None)
        material = self.request.query_params.get('material', None)  
        
        queryset = Product.objects.all().order_by('id')
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value)

        filters = Q()

        if name:
            type_search_name = self.request.query_params.get('type_search_name', 'exact')
            if type_search_name == 'exact':
                filters |= Q(name=name)
            elif type_search_name == 'contains':
                filters |= Q(name__icontains=name)
            elif type_search_name == 'startswith':
                filters |= Q(name__istartswith=name)
            elif type_search_name == 'endswith':
                filters |= Q(name__iendswith=name)
            else:
                raise ValidationError("Require name type search in ['exact', 'contains', 'startswith', 'endswith']")

        if description:
            type_search_description = self.request.query_params.get('type_search_description', 'exact')
            if type_search_description == 'exact':
                filters |= Q(description=description)
            elif type_search_description == 'contains':
                filters |= Q(description__icontains=description)
            elif type_search_description == 'startswith':
                filters |= Q(description__istartswith=description)
            elif type_search_description == 'endswith':
                filters |= Q(description__iendswith=description)
            else:
                raise ValidationError("Require description type search in ['exact', 'contains', 'startswith', 'endswith']")

        if detail_description:
            type_search_detail_description = self.request.query_params.get('type_search_detail_description', 'exact')
            if type_search_detail_description == 'exact':
                filters |= Q(detail_description=detail_description)
            elif type_search_detail_description == 'contains':
                filters |= Q(detail_description__icontains=detail_description)
            elif type_search_detail_description == 'startswith':
                filters |= Q(detail_description__istartswith=detail_description)
            elif type_search_detail_description == 'endswith':
                filters |= Q(detail_description__iendswith=detail_description)
            else:
                raise ValidationError("Require detail_description type search in ['exact', 'contains', 'startswith', 'endswith']")
        
        if category:
            type_search_category = self.request.query_params.get('type_search_category', 'exact')
            if type_search_category == 'exact':
                filters |= Q(category=category)
            elif type_search_category == 'contains':
                filters |= Q(category__icontains=category)
            elif type_search_category == 'startswith':
                filters |= Q(category__istartswith=category)
            elif type_search_category == 'endswith':
                filters |= Q(category__iendswith=category)
            else:
                raise ValidationError("Require category type search in ['exact', 'contains', 'startswith', 'endswith']")
    
        if brand:
            type_search_brand = self.request.query_params.get('type_search_brand', 'exact')
            if type_search_brand == 'exact':
                filters |= Q(brand=brand)
            elif type_search_brand == 'contains':
                filters |= Q(brand__icontains=brand)
            elif type_search_brand == 'startswith':
                filters |= Q(brand__istartswith=brand)
            elif type_search_brand == 'endswith':
                filters |= Q(brand__iendswith=brand)
            else:
                raise ValidationError("Require brand type search in ['exact', 'contains', 'startswith', 'endswith']")

        if material:
            type_search_material = self.request.query_params.get('type_search_material', 'exact')
            if type_search_material == 'exact':
                filters |= Q(material=material)
            elif type_search_material == 'contains':
                filters |= Q(material__icontains=material)
            elif type_search_material == 'startswith':
                filters |= Q(material__istartswith=material)
            elif type_search_material == 'endswith':
                filters |= Q(material__iendswith=material)
            else:
                raise ValidationError("Require material type search in ['exact', 'contains', 'startswith', 'endswith']")
        
        queryset = queryset.filter(filters)

        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

## SubProduct
class SubProductViewSet(viewsets.ModelViewSet):
    queryset = SubProduct.objects.all().order_by('id')
    serializer_class = SubProductSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        if getattr(self, 'action', None) in ['list', 'retrieval']:
            return []
        return super().get_authenticators()


    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['list', 'retrieve']:
            return []
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'soft_delete', 'multiple_delete', 'multiple_destroy']:
            return [IsAdminPermission()]  
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return SubProductUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return SubProductSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsSubProductSerializer
        return SubProductSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in SubProduct._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("subProduct list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubProductSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = SubProductSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("subProduct retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=SubProductUpdateSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("subProduct create")
        data = request.data.copy()

        # Nếu có file image thì xử lý upload
        image_file = request.FILES.get('image')
        if image_file:
            try:
                upload_url = request.build_absolute_uri('/api/upload/')
                upload_response = requests.post(
                    upload_url,
                    files={'image': image_file}
                )
                if upload_response.status_code == 200 or upload_response.status_code == 201:
                    image_url = upload_response.json().get('image_url')
                    if image_url:
                        data['image_url'] = image_url
                    else:
                        return Response({'error': 'Upload thành công nhưng không nhận được URL.'}, status=500)
                else:
                    return Response({'error': 'Lỗi khi upload ảnh.'}, status=upload_response.status_code)
            except Exception as e:
                return Response({'error': f'Lỗi upload ảnh: {str(e)}'}, status=500)

        # Xử lý product_id
        product_id = request.data.get('product_id', None)
        print("product_id", product_id)
        data_productSubProduct = {}
        if product_id!=None: 
            try:
                product = Product.objects.get(id=product_id)
                data_productSubProduct['product'] = product.id
                print("vao day")
            except Product.DoesNotExist:
                return Response({'detail': 'Product not found'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'detail': 'product_id not found'}, status=status.HTTP_404_NOT_FOUND)
            
        subProduct = SubProductSerializer(data=data)

        if subProduct.is_valid():
            subProduct.save()
            print("subProduct.data.get('id')", subProduct.data.get('id'))
            data_productSubProduct['sub_product'] = subProduct.data.get('id')
            productSubProduct = ProductSubProductSerializer(data=data_productSubProduct)
            if productSubProduct.is_valid():
                productSubProduct.save()
            else: 
                return Response(
                    {"detail": "ProductSubProduct is invalid",  "errors": productSubProduct.errors}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"detail": "SubProduct is invalid",  "errors": subProduct.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"subProduct": subProduct.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        # Xử lý product_id
        product_id = request.data.get('product_id', None)
        print("product_id", product_id)
        data_productSubProduct = {}
        if product_id!=None: 
            try:
                product = Product.objects.get(id=product_id)
                data_productSubProduct['product'] = product.id
                print("vao day")
            except Product.DoesNotExist:
                return Response({'detail': 'Product not found'}, status=status.HTTP_403_FORBIDDEN)
        product_subproducts = instance.products.select_related('product')
        if len(product_subproducts) == 1: 
            product_subproduct = product_subproducts[0]
            productSubProduct = ProductSubProductSerializer(product_subproduct, data=data_productSubProduct, partial=partial)
            productSubProduct.is_valid(raise_exception=True)
            productSubProduct.save()


        # Nếu có file image thì xử lý upload
        image_file = request.FILES.get('image')
        if image_file:
            try:
                upload_url = request.build_absolute_uri('/api/upload/')
                upload_response = requests.post(
                    upload_url,
                    files={'image': image_file}
                )
                if upload_response.status_code == 200 or upload_response.status_code == 201:
                    image_url = upload_response.json().get('image_url')
                    if image_url:
                        data['image_url'] = image_url
                    else:
                        return Response({'error': 'Upload thành công nhưng không nhận được URL.'}, status=500)
                else:
                    return Response({'error': 'Lỗi khi upload ảnh.'}, status=upload_response.status_code)
            except Exception as e:
                return Response({'error': f'Lỗi upload ảnh: {str(e)}'}, status=500)

        subProduct = SubProductSerializer(instance, data=data, partial=partial)
        subProduct.is_valid(raise_exception=True)
        subProduct.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("subProduct partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()

        # Xử lý product_id
        product_id = request.data.get('product_id', None)
        print("product_id", product_id)
        data_productSubProduct = {}
        if product_id!=None: 
            try:
                product = Product.objects.get(id=product_id)
                data_productSubProduct['product'] = product.id
                print("vao day")
            except Product.DoesNotExist:
                return Response({'detail': 'Product not found'}, status=status.HTTP_403_FORBIDDEN)
        product_subproducts = instance.products.select_related('product')
        if len(product_subproducts) == 1: 
            product_subproduct = product_subproducts[0]
            productSubProduct = ProductSubProductSerializer(product_subproduct, data=data_productSubProduct, partial=partial)
            productSubProduct.is_valid(raise_exception=True)
            productSubProduct.save()


        # Nếu có file image thì xử lý upload
        image_file = request.FILES.get('image')
        if image_file:
            try:
                upload_url = request.build_absolute_uri('/api/upload/')
                upload_response = requests.post(
                    upload_url,
                    files={'image': image_file}
                )
                if upload_response.status_code == 200 or upload_response.status_code == 201:
                    image_url = upload_response.json().get('image_url')
                    if image_url:
                        data['image_url'] = image_url
                    else:
                        return Response({'error': 'Upload thành công nhưng không nhận được URL.'}, status=500)
                else:
                    return Response({'error': 'Lỗi khi upload ảnh.'}, status=upload_response.status_code)
            except Exception as e:
                return Response({'error': f'Lỗi upload ảnh: {str(e)}'}, status=500)

        subProduct = SubProductSerializer(instance, data=data, partial=partial)
        subProduct.is_valid(raise_exception=True)
        subProduct.save()

        return Response(subProduct.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("subProduct destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = SubProduct.objects.get(id=pk)
        except SubProduct.DoesNotExist:
            return Response({'detail': 'SubProduct not found'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response({'message': 'SubProduct deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("subProduct soft_delete")
        instance = self.get_object()
        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'SubProduct already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()

        product_subproducts = instance.products.select_related('product')
        if len(product_subproducts) == 1: 
            product_subproduct = product_subproducts[0]
            if product_subproduct.status_enum != StatusEnum.DELETED.value:
                product_subproduct.status_enum = StatusEnum.DELETED.value
                product_subproduct.save()
        return Response({'detail': 'SubProduct soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_delete(self, request):
        print("subProduct multiple_delete")
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No subProduct IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

        subProducts = SubProduct.objects.filter(id__in=ids)
        if not subProducts.exists():
            return Response({'message': 'No subProducts found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)

        deleted_count = 0
        already_deleted_ids = []

        for subProduct in subProducts:
            if subProduct.status_enum == StatusEnum.DELETED.value:
                already_deleted_ids.append(subProduct.id)
                continue

            subProduct.status_enum = StatusEnum.DELETED.value
            subProduct.save()
            deleted_count += 1

            product_subproducts = subProduct.products.select_related('product')
            if len(product_subproducts) == 1:
                product_subproduct = product_subproducts[0]
                if product_subproduct.status_enum != StatusEnum.DELETED.value:
                    product_subproduct.status_enum = StatusEnum.DELETED.value
                    product_subproduct.save()

        response_data = {
            'message': f'SubProducts soft deleted: {deleted_count}',
            'already_deleted_ids': already_deleted_ids
        }
        return Response(response_data, status=status.HTTP_200_OK)

    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('subProduct multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No subProduct IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        subProducts = SubProduct.objects.filter(id__in=ids) 
        if not subProducts.exists():
            return Response({'message': 'No subProducts found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        for subProduct in subProducts:
            subProduct.delete()
        return Response({'message': 'SubProducts destroy successfully'}, status=status.HTTP_200_OK)



## ProductSubProduct
class ProductSubProductViewSet(viewsets.ModelViewSet):
    queryset = ProductSubProduct.objects.all().order_by('id')
    serializer_class = ProductSubProductSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        if getattr(self, 'action', None) in ['list', 'retrieval']:
            return []
        return super().get_authenticators()

    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['list', 'retrieve']:
            return []
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'soft_delete', 'multiple_delete', 'multiple_destroy']:
            return [IsAdminPermission()]  
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ProductSubProductUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return ProductSubProductSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsProductSubProductSerializer
        return ProductSubProductSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in ProductSubProduct._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("productSubProduct list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductSubProductSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductSubProductSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("productSubProduct retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=ProductSubProductSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("productSubProduct create")
        return Response({"message": "Method not allow"}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        productSubProduct = ProductSubProductSerializer(instance, data=data, partial=partial)
        productSubProduct.is_valid(raise_exception=True)
        productSubProduct.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("productSubProduct partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()
        
        productSubProduct = ProductSubProductSerializer(instance, data=data, partial=partial)
        productSubProduct.is_valid(raise_exception=True)
        productSubProduct.save()

        return Response(productSubProduct.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("productSubProduct destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = ProductSubProduct.objects.get(id=pk)
        except ProductSubProduct.DoesNotExist:
            return Response({'detail': 'ProductSubProduct not found'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response({'message': 'ProductSubProduct deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("productSubProduct soft_delete")
        instance = self.get_object()
        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'ProductSubProduct already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()
        return Response({'detail': 'ProductSubProduct soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_delete(self, request):
        print("productSubProduct multiple_delete")
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No productSubProduct IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        productSubProducts = ProductSubProduct.objects.filter(id__in=ids) 
        if not productSubProducts.exists():
            return Response({'message': 'No productSubProducts found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        productSubProducts.update(status_enum=StatusEnum.DELETED.value)
        return Response({'message': 'ProductSubProducts soft deleted successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('productSubProduct multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No productSubProduct IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        productSubProducts = ProductSubProduct.objects.filter(id__in=ids) 
        if not productSubProducts.exists():
            return Response({'message': 'No productSubProducts found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        for productSubProduct in productSubProducts:
            productSubProduct.delete()
        return Response({'message': 'ProductSubProducts destroy successfully'}, status=status.HTTP_200_OK)

