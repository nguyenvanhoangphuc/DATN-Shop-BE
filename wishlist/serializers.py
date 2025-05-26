from rest_framework import serializers
from .models import WishList
from django.contrib.auth.hashers import make_password
from products.serializers import *

class WishListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishList
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class WishListSerializerOutput(serializers.ModelSerializer):
    sub_product = SubProductSerializerOutput()
    class Meta:
        model = WishList
        fields = ('id', 'user', 'sub_product', 'status_enum')
        read_only_fields = ('id', 'created_at')

class WishListUpdateSerializer(serializers.ModelSerializer):
    sub_product_id = serializers.IntegerField()
    class Meta:
        model = WishList
        fields = ('sub_product_id',)
    
class IdsWishListSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

