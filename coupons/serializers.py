from rest_framework import serializers
from .models import Coupon
from django.contrib.auth.hashers import make_password

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'

class CouponSerializerOutput(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ('id', 'code', 'discount_percentage', 'quantity', 'valid_from', 'valid_until', 'status_enum')

class CouponUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ('code', 'discount_percentage', 'quantity', 'valid_from', 'valid_until')
    
class IdsCouponSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

