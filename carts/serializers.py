from rest_framework import serializers
from .models import CartItem
from django.contrib.auth.hashers import make_password
from products.serializers import *

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class CartItemSerializerOutput(serializers.ModelSerializer):
    sub_product = SubProductSerializerOutput()
    class Meta:
        model = CartItem
        fields = ('id', 'user', 'sub_product', 'quantity', 'status_enum')
        read_only_fields = ('id', 'created_at')

class CartItemUpdateSerializer(serializers.ModelSerializer):
    sub_product_id = serializers.IntegerField()
    class Meta:
        model = CartItem
        fields = ('sub_product_id', 'quantity')
    
class IdsCartItemSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

