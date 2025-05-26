from rest_framework import serializers
from .models import Review
from django.contrib.auth.hashers import make_password
from products.serializers import *

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class ReviewSerializerOutput(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('id', 'user', 'sub_product', 'rating', 'comment', 'created_at', 'status_enum')
        read_only_fields = ('id', 'created_at')

class ReviewUpdateSerializer(serializers.ModelSerializer):
    sub_product_id = serializers.IntegerField()
    class Meta:
        model = Review
        fields = ('sub_product_id', 'rating', 'comment')
    
class IdsReviewSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

