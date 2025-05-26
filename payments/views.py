from django.db.models import Q
from rest_framework.response import Response
from rest_framework import viewsets, generics, status
from rest_framework.exceptions import ValidationError
from payments.serializers import PaymentMethodSerializer, PaymentMethodSerializerOutput, PaymentMethodUpdateSerializer, IdsPaymentMethodSerializer, PaymentSerializer, PaymentSerializerOutput, PaymentUpdateSerializer, IdsPaymentSerializer
from app.serializers import ResponseSerializer
from payments.models import PaymentMethod, Payment, StatusEnum
from orders.models import Order
import requests
from rest_framework.decorators import action
from authentication.permissions import IsCustomerPermission, IsAdminPermission, IsAuthenticatedPermission
from drf_yasg.utils import swagger_auto_schema

class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all().order_by('id')
    serializer_class = PaymentMethodSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        if getattr(self, 'action', None) in ['list', 'retrieval']:
            return []
        return super().get_authenticators()

    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['list', 'retrieve']:
            return []
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'soft_delete', 'multiple_delete', 'multiple_destroy']:
            return [IsAdminPermission()]  
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return PaymentMethodUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return PaymentMethodSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsPaymentMethodSerializer
        return PaymentMethodSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in PaymentMethod._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("paymentMethod list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PaymentMethodSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PaymentMethodSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("paymentMethod retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=PaymentMethodUpdateSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("paymentMethod create")
        data = request.data.copy()

        # Nếu có file image thì xử lý upload
        image_file = request.FILES.get('image')
        if image_file:
            try:
                upload_url = request.build_absolute_uri('/api/upload/')
                upload_response = requests.post(
                    upload_url,
                    files={'image': image_file}
                )
                if upload_response.status_code == 200 or upload_response.status_code == 201:
                    image_url = upload_response.json().get('image_url')
                    if image_url:
                        data['image_url'] = image_url
                    else:
                        return Response({'error': 'Upload thành công nhưng không nhận được URL.'}, status=500)
                else:
                    return Response({'error': 'Lỗi khi upload ảnh.'}, status=upload_response.status_code)
            except Exception as e:
                return Response({'error': f'Lỗi upload ảnh: {str(e)}'}, status=500)

        paymentMethod = PaymentMethodSerializer(data=data)
        if paymentMethod.is_valid():
            paymentMethod.save()
        else:
            return Response(
                {"detail": "PaymentMethod is invalid",  "errors": paymentMethod.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"paymentMethod": paymentMethod.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        # Nếu có file image thì xử lý upload
        image_file = request.FILES.get('image')
        if image_file:
            try:
                upload_url = request.build_absolute_uri('/api/upload/')
                upload_response = requests.post(
                    upload_url,
                    files={'image': image_file}
                )
                if upload_response.status_code == 200 or upload_response.status_code == 201:
                    image_url = upload_response.json().get('image_url')
                    if image_url:
                        data['image_url'] = image_url
                    else:
                        return Response({'error': 'Upload thành công nhưng không nhận được URL.'}, status=500)
                else:
                    return Response({'error': 'Lỗi khi upload ảnh.'}, status=upload_response.status_code)
            except Exception as e:
                return Response({'error': f'Lỗi upload ảnh: {str(e)}'}, status=500)

        paymentMethod = PaymentMethodSerializer(instance, data=data, partial=partial)
        paymentMethod.is_valid(raise_exception=True)
        paymentMethod.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("paymentMethod partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()
        # Nếu có file image thì xử lý upload
        image_file = request.FILES.get('image')
        if image_file:
            try:
                upload_url = request.build_absolute_uri('/api/upload/')
                upload_response = requests.post(
                    upload_url,
                    files={'image': image_file}
                )
                if upload_response.status_code == 200 or upload_response.status_code == 201:
                    image_url = upload_response.json().get('image_url')
                    if image_url:
                        data['image_url'] = image_url
                    else:
                        return Response({'error': 'Upload thành công nhưng không nhận được URL.'}, status=500)
                else:
                    return Response({'error': 'Lỗi khi upload ảnh.'}, status=upload_response.status_code)
            except Exception as e:
                return Response({'error': f'Lỗi upload ảnh: {str(e)}'}, status=500)
        # serializer = self.get_serializer(instance, data=data, partial=partial)
        # serializer.is_valid(raise_exception=True)
        # self.perform_update(serializer)
        paymentMethod = PaymentMethodSerializer(instance, data=data, partial=partial)
        paymentMethod.is_valid(raise_exception=True)
        paymentMethod.save()

        return Response(paymentMethod.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("paymentMethod destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = PaymentMethod.objects.get(id=pk)
        except PaymentMethod.DoesNotExist:
            return Response({'detail': 'PaymentMethod not found'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response({'message': 'PaymentMethod deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("paymentMethod soft_delete")
        instance = self.get_object()
        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'PaymentMethod already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()
        return Response({'detail': 'PaymentMethod soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_delete(self, request):
        print("paymentMethod multiple_delete")
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No paymentMethod IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        paymentMethods = PaymentMethod.objects.filter(id__in=ids) 
        if not paymentMethods.exists():
            return Response({'message': 'No paymentMethods found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        paymentMethods.update(status_enum=StatusEnum.DELETED.value)
        return Response({'message': 'PaymentMethods soft deleted successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('paymentMethod multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No paymentMethod IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        paymentMethods = PaymentMethod.objects.filter(id__in=ids) 
        if not paymentMethods.exists():
            return Response({'message': 'No paymentMethods found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        for paymentMethod in paymentMethods:
            paymentMethod.delete()
        return Response({'message': 'PaymentMethods destroy successfully'}, status=status.HTTP_200_OK)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().order_by('id')
    serializer_class = PaymentSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        return super().get_authenticators()


    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['create', 'update', 'partial_update', 'soft_delete', 'destroy', 'multiple_delete', 'multiple_destroy']: 
            return [(IsCustomerPermission)()]
        elif self.action in ['list', 'retrieve']:
            return [IsAdminPermission()] 
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return PaymentUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return PaymentSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsPaymentSerializer
        return PaymentSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in Payment._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("payment list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PaymentSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PaymentSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("payment retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=PaymentUpdateSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("payment create")
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
        
        # check payment_method_id is valid
        if 'payment_method_id' not in request.data:
            return Response({'detail': 'PaymentMethod ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        payment_method_id = request.data.get('payment_method_id', None)
        print("payment_method_id", payment_method_id)
        if payment_method_id!=None: 
            try:
                payment_method = PaymentMethod.objects.get(id=payment_method_id)
                data['payment_method'] = payment_method.id
            except PaymentMethod.DoesNotExist:
                return Response({'detail': 'PaymentMethod not found'}, status=status.HTTP_403_FORBIDDEN) 
        payment = PaymentSerializer(data=data)
        if payment.is_valid():
            payment.save()
        else:
            return Response(
                {"detail": "Payment is invalid",  "errors": payment.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"payment": payment.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if user_id != instance.order.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        payment_method_id = request.data.get('payment_method_id', None)
        print("payment_method_id", payment_method_id)
        if payment_method_id!=None: 
            try:
                payment_method = PaymentMethod.objects.get(id=payment_method_id)
                data['payment_method'] = payment_method.id
            except PaymentMethod.DoesNotExist:
                return Response({'detail': 'PaymentMethod not found'}, status=status.HTTP_403_FORBIDDEN) 

        payment = PaymentSerializer(instance, data=data, partial=partial)
        payment.is_valid(raise_exception=True)
        payment.save()

        paymentModel = Payment.objects.get(id=payment.data.get('id'))

        paymentOutput = PaymentSerializerOutput(paymentModel)
    
        return Response(paymentOutput.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("payment partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if user_id != instance.order.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        payment_method_id = request.data.get('payment_method_id', None)
        print("payment_method_id", payment_method_id)
        if payment_method_id!=None: 
            try:
                payment_method = PaymentMethod.objects.get(id=payment_method_id)
                data['payment_method'] = payment_method.id
            except PaymentMethod.DoesNotExist:
                return Response({'detail': 'PaymentMethod not found'}, status=status.HTTP_403_FORBIDDEN) 

        payment = PaymentSerializer(instance, data=data, partial=partial)
        payment.is_valid(raise_exception=True)
        payment.save()

        paymentModel = Payment.objects.get(id=payment.data.get('id'))

        paymentOutput = PaymentSerializerOutput(paymentModel)
    
        return Response(paymentOutput.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("payment destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = Payment.objects.get(id=pk)
        except Payment.DoesNotExist:
            return Response({'detail': 'Payment not found'}, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.user.id
        if user_id != instance.order.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        instance.delete()
        return Response({'message': 'Payment deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("payment soft_delete")
        instance = self.get_object()

        user_id = request.user.id
        if user_id != instance.order.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'Payment already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()
        return Response({'detail': 'Payment soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_delete(self, request):
        print("payment multiple_delete")

        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No payment IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        payments = Payment.objects.filter(id__in=ids) 
        if not payments.exists():
            return Response({'message': 'No payments found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for instance in payments: 
            if user_id != instance.order.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)

        payments.update(status_enum=StatusEnum.DELETED.value)
        return Response({'message': 'Payments soft deleted successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('payment multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No payment IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        payments = Payment.objects.filter(id__in=ids) 
        if not payments.exists():
            return Response({'message': 'No payments found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for payment in payments:
            if user_id != payment.order.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)
            payment.delete()

        return Response({'message': 'Payments destroy successfully'}, status=status.HTTP_200_OK)
    