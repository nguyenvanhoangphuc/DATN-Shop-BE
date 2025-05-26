from rest_framework.response import Response
from rest_framework import viewsets, status
from shipping.serializers import ShippingSerializer, ShippingSerializerOutput, ShippingUpdateSerializer, IdsShippingSerializer
from app.serializers import ResponseSerializer
from shipping.models import Shipping, StatusEnum
from orders.models import Order
from rest_framework.decorators import action
from authentication.permissions import IsCustomerPermission, IsAdminPermission, IsAuthenticatedPermission
from drf_yasg.utils import swagger_auto_schema


class ShippingViewSet(viewsets.ModelViewSet):
    queryset = Shipping.objects.all().order_by('id')
    serializer_class = ShippingSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        return super().get_authenticators()


    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['create']: 
            return [(IsCustomerPermission)()]
        if self.action in ['update', 'partial_update', 'soft_delete', 'destroy', 'multiple_delete', 'multiple_destroy']: 
            return [(IsCustomerPermission | IsAdminPermission)()]
        elif self.action in ['list', 'retrieve']:
            return [IsAdminPermission()] 
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ShippingUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return ShippingSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsShippingSerializer
        return ShippingSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in Shipping._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("shipping list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ShippingSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ShippingSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("shipping retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=ShippingUpdateSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("shipping create")
        data = request.data.copy()
        user_id = request.user.id
        data['user'] = user_id

        order_id = request.data.get('order_id', None)
        if order_id is None:
            return Response({'detail': 'Order ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # check user has permission to create order item
        try:
            order = Order.objects.get(id=order_id, user_id=user_id, status_enum=StatusEnum.ACTIVE.value)
            data['order'] = order.id
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found or you do not have permission to access it'}, status=status.HTTP_403_FORBIDDEN)
        
        shipping = ShippingSerializer(data=data)
        if shipping.is_valid():
            shipping.save()
        else:
            return Response(
                {"detail": "Shipping is invalid",  "errors": shipping.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"shipping": shipping.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if request.user.role != 'admin' and user_id != instance.order.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        order_id = request.data.get('order_id', None)
        if order_id is not None:
            return Response({'detail': 'Order ID cannot be updated'}, status=status.HTTP_400_BAD_REQUEST)
        
        # status only apply for admin
        status_value = request.data.get('status', None)
        if status_value is not None:
            if request.user.role == 'admin':
                data['status'] = status_value
            else:
                return Response({'detail': 'You do not have permission to update status'}, status=status.HTTP_403_FORBIDDEN)


        shipping = ShippingSerializer(instance, data=data, partial=partial)
        shipping.is_valid(raise_exception=True)
        shipping.save()

        shippingModel = Shipping.objects.get(id=shipping.data.get('id'))

        shippingOutput = ShippingSerializerOutput(shippingModel)
    
        return Response(shippingOutput.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("shipping partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if request.user.role != 'admin' and user_id != instance.order.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        order_id = request.data.get('order_id', None)
        if order_id is not None:
            return Response({'detail': 'Order ID cannot be updated'}, status=status.HTTP_400_BAD_REQUEST)
        
        # status only apply for admin
        status_value = request.data.get('status', None)
        if status_value is not None:
            if request.user.role == 'admin':
                data['status'] = status_value
            else:
                return Response({'detail': 'You do not have permission to update status'}, status=status.HTTP_403_FORBIDDEN)

        shipping = ShippingSerializer(instance, data=data, partial=partial)
        shipping.is_valid(raise_exception=True)
        shipping.save()

        shippingModel = Shipping.objects.get(id=shipping.data.get('id'))

        shippingOutput = ShippingSerializerOutput(shippingModel)
    
        return Response(shippingOutput.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("shipping destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = Shipping.objects.get(id=pk)
        except Shipping.DoesNotExist:
            return Response({'detail': 'Shipping not found'}, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.user.id
        if request.user.role != 'admin' and user_id != instance.order.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        instance.delete()
        return Response({'message': 'Shipping deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("shipping soft_delete")
        instance = self.get_object()

        user_id = request.user.id
        if request.user.role != 'admin' and user_id != instance.order.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'Shipping already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()
        return Response({'detail': 'Shipping soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_delete(self, request):
        print("shipping multiple_delete")

        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No shipping IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        shippings = Shipping.objects.filter(id__in=ids) 
        if not shippings.exists():
            return Response({'message': 'No shippings found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for instance in shippings: 
            if request.user.role != 'admin' and user_id != instance.order.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)

        shippings.update(status_enum=StatusEnum.DELETED.value)
        return Response({'message': 'Shippings soft deleted successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('shipping multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No shipping IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        shippings = Shipping.objects.filter(id__in=ids) 
        if not shippings.exists():
            return Response({'message': 'No shippings found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for shipping in shippings:
            if request.user.role != 'admin' and user_id != shipping.order.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)
            shipping.delete()

        return Response({'message': 'Shippings destroy successfully'}, status=status.HTTP_200_OK)
    