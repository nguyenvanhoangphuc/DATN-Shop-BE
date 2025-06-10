from django.db.models import Q
from rest_framework.response import Response
from rest_framework import viewsets, generics, status
from rest_framework.exceptions import ValidationError
from carts.serializers import CartItemSerializer, CartItemSerializerOutput, CartItemUpdateSerializer, IdsCartItemSerializer
from app.serializers import ResponseSerializer
from carts.models import CartItem, StatusEnum
from products.models import SubProduct
import requests
from rest_framework.decorators import action
from authentication.permissions import IsCustomerPermission, IsAdminPermission, IsAuthenticatedPermission
from drf_yasg.utils import swagger_auto_schema

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all().order_by('id')
    serializer_class = CartItemSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        return super().get_authenticators()


    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['create', 'update', 'partial_update', 'soft_delete', 'destroy', 'multiple_delete', 'multiple_destroy', 'my_cart']: 
            return [(IsCustomerPermission)()]
        elif self.action in ['list', 'retrieve']:
            return [IsAdminPermission()] 
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return CartItemUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return CartItemSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsCartItemSerializer
        return CartItemSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in CartItem._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("cartItem list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CartItemSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CartItemSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("cartItem retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=CartItemUpdateSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("cartItem create")
        data = request.data.copy()
        user_id = request.user.id
        data['user'] = user_id
        sub_product_id = request.data.get('sub_product_id', None)
        print("sub_product_id", sub_product_id)
        if sub_product_id!=None: 
            try:
                sub_product = SubProduct.objects.get(id=sub_product_id)
                data['sub_product'] = sub_product.id
            except SubProduct.DoesNotExist:
                return Response({'detail': 'SubProduct not found'}, status=status.HTTP_403_FORBIDDEN) 
        # Check if the user already has a cart item for this sub_product
        existing_cart_item = CartItem.objects.filter(
            user=user_id, 
            sub_product=sub_product_id 
        ).first()

        if existing_cart_item:
            if existing_cart_item.status_enum == StatusEnum.DELETED.value:
                existing_cart_item.status_enum = StatusEnum.ACTIVE.value
                existing_cart_item.save()
                cartItem = CartItemSerializerOutput(existing_cart_item)
                return Response({"cartItem": cartItem.data}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "Bạn đã có sản phẩm này trong giỏ hàng."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        cartItem = CartItemSerializer(data=data)
        if cartItem.is_valid():
            cartItem.save()
        else:
            return Response(
                {"detail": "CartItem is invalid",  "errors": cartItem.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"cartItem": cartItem.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if user_id != instance.user.id: 
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        cartItem = CartItemSerializer(instance, data=data, partial=partial)
        cartItem.is_valid(raise_exception=True)
        cartItem.save()

        cartItemModel = CartItem.objects.get(id=cartItem.data.get('id'))

        cartItemOutput = CartItemSerializerOutput(cartItemModel)
    
        return Response(cartItemOutput.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("cartItem partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        cartItem = CartItemSerializer(instance, data=data, partial=partial)
        cartItem.is_valid(raise_exception=True)
        cartItem.save()

        cartItemModel = CartItem.objects.get(id=cartItem.data.get('id'))

        cartItemOutput = CartItemSerializerOutput(cartItemModel)
    
        return Response(cartItemOutput.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("cartItem destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = CartItem.objects.get(id=pk)
        except CartItem.DoesNotExist:
            return Response({'detail': 'CartItem not found'}, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        instance.delete()
        return Response({'message': 'CartItem deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("cartItem soft_delete")
        instance = self.get_object()

        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'CartItem already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()
        return Response({'detail': 'CartItem soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_delete(self, request):
        print("cartItem multiple_delete")

        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No cartItem IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        cartItems = CartItem.objects.filter(id__in=ids) 
        if not cartItems.exists():
            return Response({'message': 'No cartItems found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for instance in cartItems: 
            if user_id != instance.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)

        cartItems.update(status_enum=StatusEnum.DELETED.value)
        return Response({'message': 'CartItems soft deleted successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('cartItem multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No cartItem IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        cartItems = CartItem.objects.filter(id__in=ids) 
        if not cartItems.exists():
            return Response({'message': 'No cartItems found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for cartItem in cartItems:
            if user_id != cartItem.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)
            cartItem.delete()

        return Response({'message': 'CartItems destroy successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['get'], url_path='my-cart')
    @swagger_auto_schema(
        responses={200: CartItemSerializerOutput}
    )
    def my_cart(self, request):
        print('cartItem my_cart')

        user_id = request.user.id
        # print("user_id", user_id)
        # try:
        #     cartItems = self.queryset.filter(user=user_id)
        # except CartItem.DoesNotExist: 
        #     return Response({'detail': 'No item found in my cart'}, status=status.HTTP_403_FORBIDDEN) 
        cartItems = self.queryset.filter(user=user_id, status_enum=StatusEnum.ACTIVE.value)

        if not cartItems.exists():
            # return Response({'detail': 'No item found in my cart'}, status=status.HTTP_404_NOT_FOUND)
            return Response([], status=status.HTTP_200_OK)  # Return empty list if no items found

        # print("cartItems", cartItems)
        cartItemOutput = CartItemSerializerOutput(cartItems, many=True)

        return Response(cartItemOutput.data, status=status.HTTP_200_OK)

