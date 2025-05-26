from django.db.models import Q
from rest_framework.response import Response
from rest_framework import viewsets, generics, status
from rest_framework.exceptions import ValidationError
from coupons.serializers import CouponSerializer, CouponSerializerOutput, CouponUpdateSerializer, IdsCouponSerializer
from app.serializers import ResponseSerializer
from coupons.models import Coupon, StatusEnum
import requests
from rest_framework.decorators import action
from authentication.permissions import IsCustomerPermission, IsAdminPermission, IsAuthenticatedPermission
from drf_yasg.utils import swagger_auto_schema

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        # if getattr(self, 'action', None) == 'create':
        #     return []
        return super().get_authenticators()


    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['retrieve', 'list']:
            return [(IsCustomerPermission | IsAdminPermission)()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'soft_delete', 'multiple_delete', 'multiple_destroy']:
            return [IsAdminPermission()]
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return CouponUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return CouponSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsCouponSerializer
        return CouponSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in Coupon._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    # read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("coupon list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CouponSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CouponSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("coupon retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=CouponSerializer,
        responses={200: CouponSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("coupon create")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        coupon = CouponSerializer(instance, data=data, partial=partial)
        coupon.is_valid(raise_exception=True)
        coupon.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("coupon partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()
        
        coupon = CouponSerializer(instance, data=data, partial=partial)
        coupon.is_valid(raise_exception=True)
        coupon.save()

        return Response(coupon.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("coupon destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = Coupon.objects.get(id=pk)
        except Coupon.DoesNotExist:
            return Response({'message': 'Coupon not found'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response({'message': 'Coupon deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("coupon soft_delete")
        instance = self.get_object()
        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'message': 'Coupon already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()
        return Response({'message': 'Coupon soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_delete(self, request):
        print("coupon multiple_delete")
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No coupon IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        coupons = Coupon.objects.filter(id__in=ids) 
        if not coupons.exists():
            return Response({'message': 'No coupons found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        coupons.update(status_enum=StatusEnum.DELETED.value)
        return Response({'message': 'Coupons soft deleted successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('coupon multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No coupon IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        coupons = Coupon.objects.filter(id__in=ids) 
        if not coupons.exists():
            return Response({'message': 'No coupons found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        for coupon in coupons:
            coupon.delete()
        return Response({'message': 'Coupons destroy successfully'}, status=status.HTTP_200_OK)
