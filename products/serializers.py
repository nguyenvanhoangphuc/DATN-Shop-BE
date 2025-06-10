from rest_framework import serializers
from .models import Product, Category, Material, Brand, SubProduct, ProductSubProduct
from django.contrib.auth.hashers import make_password
from app.models import StatusEnum
from django.db.models import Min, Max, Sum

## Category
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CategorySerializerOutput(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'parent', 'status_enum')

class CategoryUpdateSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField()
    class Meta:
        model = Category
        fields = ('name', 'description', 'parent_id')
    
class IdsCategorySerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

## Material
class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class MaterialSerializerOutput(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ('id', 'name', 'description', 'status_enum')

class MaterialUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ('name', 'description')
    
class IdsMaterialSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

## Brand
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class BrandSerializerOutput(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name', 'description', 'status_enum')

class BrandUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('name', 'description')
    
class IdsBrandSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)


## Product
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class ProductSerializerOutput(serializers.ModelSerializer):
    min_price = serializers.SerializerMethodField()
    max_price = serializers.SerializerMethodField()
    sold_per_month = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'detail_description', 'category', 'brand', 'material', 'image_url', 'min_price', 'max_price', 'sold_per_month')
        read_only_fields = ('id', 'created_at')

    def get_min_price(self, obj):
        return ProductSubProduct.objects.filter(
            product=obj,
            status_enum=StatusEnum.ACTIVE,
            sub_product__status_enum=StatusEnum.ACTIVE
        ).aggregate(min_price=Min('sub_product__price'))['min_price']

    def get_max_price(self, obj):
        return ProductSubProduct.objects.filter(
            product=obj,
            status_enum=StatusEnum.ACTIVE,
            sub_product__status_enum=StatusEnum.ACTIVE
        ).aggregate(max_price=Max('sub_product__price'))['max_price']
    
    def get_sold_per_month(self, obj):
        return ProductSubProduct.objects.filter(
            product=obj,
            status_enum=StatusEnum.ACTIVE,
            sub_product__status_enum=StatusEnum.ACTIVE
        ).aggregate(sold_per_month=Sum('sub_product__saled_per_month'))['sold_per_month']

class ProductUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    class Meta:
        model = Product
        fields = ('name', 'description', 'detail_description', 'category', 'brand', 'material', 'image')
        read_only_fields = ('id', 'created_at')
    
class IdsProductSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)


## SubProduct
class SubProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubProduct
        fields = '__all__'

class SubProductSerializerOutput(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = SubProduct
        fields = (
            'id', 'product', 'color', 'size', 'old_price',
            'discount_percentage', 'price', 'stock', 'image_url',
            'saled_per_month', 'status_enum'
        )

    def get_product(self, obj):
        try:
            product_subproduct = obj.products.select_related('product').first()
            if product_subproduct:
                return ProductSerializerOutput(product_subproduct.product).data
            return None
        except ProductSubProduct.DoesNotExist:
            return None

class SubProductUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    product_id = serializers.IntegerField()
    class Meta:
        model = SubProduct
        fields = ('color', 'size', 'old_price', 'discount_percentage', 'price', 'stock', 'image', 'saled_per_month', 'product_id')
    
class IdsSubProductSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)


## ProductSubProduct
class ProductSubProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSubProduct
        fields = '__all__'

class ProductSubProductSerializerOutput(serializers.ModelSerializer):
    class Meta:
        model = ProductSubProduct
        fields = ('id', 'product', 'sub_product', 'status_enum')

class ProductSubProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSubProduct
        fields = ('product', 'sub_product')
    
class IdsProductSubProductSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)


class ProductSerializerDetail(serializers.ModelSerializer):
    min_price = serializers.SerializerMethodField()
    max_price = serializers.SerializerMethodField()
    sold_per_month = serializers.SerializerMethodField()
    sub_products = serializers.SerializerMethodField()
    category = CategorySerializerOutput(read_only=True)
    brand = BrandSerializerOutput(read_only=True)
    material = MaterialSerializerOutput(read_only=True)
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'detail_description', 'category', 'brand', 'material', 'image_url', 'min_price', 'max_price', 'sold_per_month', 'sub_products')
        read_only_fields = ('id', 'created_at')

    def get_min_price(self, obj):
        return ProductSubProduct.objects.filter(
            product=obj,
            status_enum=StatusEnum.ACTIVE,
            sub_product__status_enum=StatusEnum.ACTIVE
        ).aggregate(min_price=Min('sub_product__price'))['min_price']

    def get_max_price(self, obj):
        return ProductSubProduct.objects.filter(
            product=obj,
            status_enum=StatusEnum.ACTIVE,
            sub_product__status_enum=StatusEnum.ACTIVE
        ).aggregate(max_price=Max('sub_product__price'))['max_price']
    
    def get_sold_per_month(self, obj):
        return ProductSubProduct.objects.filter(
            product=obj,
            status_enum=StatusEnum.ACTIVE,
            sub_product__status_enum=StatusEnum.ACTIVE
        ).aggregate(sold_per_month=Sum('sub_product__saled_per_month'))['sold_per_month']
    
    def get_sub_products(self, obj):
        # Lấy tất cả các SubProduct liên kết với Product này
        # và có trạng thái ACTIVE thông qua ProductSubProduct
        sub_products = SubProduct.objects.filter(
            products__product=obj,
            products__status_enum=StatusEnum.ACTIVE,
            status_enum=StatusEnum.ACTIVE
        ).distinct()

        return SubProductSerializer(sub_products, many=True).data
    