from rest_framework import serializers
from .models import Product, Category, Material, Brand, SubProduct, ProductSubProduct
from django.contrib.auth.hashers import make_password

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
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'detail_description', 'category', 'brand', 'material', 'image_url')
        read_only_fields = ('id', 'created_at')

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