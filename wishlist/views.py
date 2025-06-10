from django.db.models import Q
from rest_framework.response import Response
from rest_framework import viewsets, generics, status
from rest_framework.exceptions import ValidationError
from wishlist.serializers import WishListSerializer, WishListSerializerOutput, WishListUpdateSerializer, IdsWishListSerializer
from app.serializers import ResponseSerializer
from wishlist.models import WishList, StatusEnum
from products.models import SubProduct
from rest_framework.decorators import action
from authentication.permissions import IsCustomerPermission, IsAdminPermission, IsAuthenticatedPermission
from drf_yasg.utils import swagger_auto_schema

class WishListViewSet(viewsets.ModelViewSet):
    queryset = WishList.objects.all().order_by('id')
    serializer_class = WishListSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        return super().get_authenticators()


    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['create', 'update', 'partial_update', 'soft_delete', 'destroy', 'multiple_delete', 'multiple_destroy', 'my_wishlist']: 
            return [(IsCustomerPermission)()]
        elif self.action in ['list', 'retrieve']:
            return [IsAdminPermission()] 
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return WishListUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return WishListSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsWishListSerializer
        return WishListSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in WishList._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("wishList list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = WishListSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = WishListSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("wishList retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=WishListUpdateSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("wishList create")
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
        wishList = WishListSerializer(data=data)
        print("data", data)
        if wishList.is_valid():
            wishList.save()
        else:
            return Response(
                {"detail": "WishList is invalid",  "errors": wishList.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"wishList": wishList.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if user_id != instance.user.id: 
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        wishList = WishListSerializer(instance, data=data, partial=partial)
        wishList.is_valid(raise_exception=True)
        wishList.save()

        wishListModel = WishList.objects.get(id=wishList.data.get('id'))

        wishListOutput = WishListSerializerOutput(wishListModel)
    
        return Response(wishListOutput.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("wishList partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        wishList = WishListSerializer(instance, data=data, partial=partial)
        wishList.is_valid(raise_exception=True)
        wishList.save()

        wishListModel = WishList.objects.get(id=wishList.data.get('id'))

        wishListOutput = WishListSerializerOutput(wishListModel)
    
        return Response(wishListOutput.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("wishList destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = WishList.objects.get(id=pk)
        except WishList.DoesNotExist:
            return Response({'detail': 'WishList not found'}, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        instance.delete()
        return Response({'message': 'WishList deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("wishList soft_delete")
        instance = self.get_object()

        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'WishList already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()
        return Response({'detail': 'WishList soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_delete(self, request):
        print("wishList multiple_delete")

        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No wishList IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        wishLists = WishList.objects.filter(id__in=ids) 
        if not wishLists.exists():
            return Response({'message': 'No wishLists found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for instance in wishLists: 
            if user_id != instance.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)

        wishLists.update(status_enum=StatusEnum.DELETED.value)
        return Response({'message': 'WishLists soft deleted successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('wishList multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No wishList IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        wishLists = WishList.objects.filter(id__in=ids) 
        if not wishLists.exists():
            return Response({'message': 'No wishLists found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for wishList in wishLists:
            if user_id != wishList.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)
            wishList.delete()

        return Response({'message': 'WishLists destroy successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['get'], url_path='my-wishlist')
    @swagger_auto_schema(
        responses={200: WishListSerializerOutput}
    )
    def my_wishlist(self, request):
        print('wishList my_wishlist')

        user_id = request.user.id
        # print("user_id", user_id)
        # try:
        #     wishLists = self.queryset.filter(user=user_id)
        # except WishList.DoesNotExist: 
        #     return Response({'detail': 'No item found in my wishlist'}, status=status.HTTP_403_FORBIDDEN) 
        wishLists = self.queryset.filter(user=user_id, status_enum=StatusEnum.ACTIVE.value)

        if not wishLists.exists():
            return Response({'detail': 'No item found in my wishlist'}, status=status.HTTP_404_NOT_FOUND)

        # print("wishLists", wishLists)
        wishListOutput = WishListSerializerOutput(wishLists, many=True)

        return Response(wishListOutput.data, status=status.HTTP_200_OK)

