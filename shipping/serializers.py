from rest_framework import serializers
from .models import Shipping
from django.contrib.auth.hashers import make_password


## Shipping Serializers
class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = '__all__'

class ShippingSerializerOutput(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = ('id', 'order', 'tracking_number', 'estimated_delivery_date', 'status', 'created_at', 'status_enum')

class ShippingUpdateSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(required=True)
    class Meta:
        model = Shipping
        fields = ('order_id', 'tracking_number', 'estimated_delivery_date', 'status')
    
class IdsShippingSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)


