from rest_framework import serializers
from .models import PaymentMethod, Payment
from django.contrib.auth.hashers import make_password

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class PaymentMethodSerializerOutput(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ('id', 'name', 'description', 'image_url', 'created_at', 'status_enum')
        read_only_fields = ('id', 'created_at')

class PaymentMethodUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = PaymentMethod
        fields = ('name', 'description', 'image')
        read_only_fields = ('id', 'created_at')
    
class IdsPaymentMethodSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)



## Payment Serializers

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class PaymentSerializerOutput(serializers.ModelSerializer):
    payment_method = PaymentMethodSerializerOutput()
    class Meta:
        model = Payment
        fields = ('id', 'order', 'payment_method', 'status', 'transaction_id', 'created_at', 'status_enum')

class PaymentUpdateSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(required=True)
    payment_method_id = serializers.IntegerField(required=True)
    class Meta:
        model = Payment
        fields = ('order_id', 'payment_method_id', 'status', 'transaction_id')
    
class IdsPaymentSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)


