from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import SubProductSerializerOutput
from django.contrib.auth.hashers import make_password

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class OrderSerializerOutput(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ('id', 'user', 'subtotal', 'tax', 'discount', 'shipping_cost', 'total_price', 'status', 'created_at', 'status_enum', 'order_items')
        read_only_fields = ('id', 'created_at')

    def get_order_items(self, obj):
        order_items = obj.order_items.all()
        return OrderItemSerializerOutput(order_items, many=True).data

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('subtotal', 'tax', 'discount', 'shipping_cost', 'total_price', 'status')
        read_only_fields = ('id', 'created_at')
    
class IdsOrderSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

## Order Item Serializers

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderItemSerializerOutput(serializers.ModelSerializer):
    sub_product = SubProductSerializerOutput()
    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'sub_product', 'quantity', 'price', 'status_enum')

class OrderItemUpdateSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(required=True)
    sub_product_id = serializers.IntegerField(required=True)
    class Meta:
        model = OrderItem
        fields = ('order_id', 'sub_product_id', 'quantity', 'price')
    
class IdsOrderItemSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

