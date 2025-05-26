from django.db.models import Q
from rest_framework.response import Response
from rest_framework import viewsets, generics, status
from rest_framework.exceptions import ValidationError
from users.serializers import UserSerializer, UserSerializerOutput, UserUpdateSerializer, IdsUserSerializer
from app.serializers import ResponseSerializer
from users.models import User, StatusEnum
import requests
from rest_framework.decorators import action
from authentication.permissions import IsCustomerPermission, IsAdminPermission, IsAuthenticatedPermission
from drf_yasg.utils import swagger_auto_schema

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        if getattr(self, 'action', None) == 'create':
            return []
        return super().get_authenticators()


    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action == 'create':
            return [] 
        elif self.action == 'list':
            return [(IsCustomerPermission | IsAdminPermission)()]  # Chỉ admin mới được xem danh sách user
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'soft_delete']:
            return [(IsAuthenticatedPermission | IsAdminPermission)()]  # Chính mình hoặc admin
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return [IsAdminPermission()] # Chỉ admin mới được phép xóa nhiều user
        elif self.action == 'me':
            return [IsAuthenticatedPermission()]
        return [IsAuthenticatedPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return UserSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsUserSerializer
        return UserSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in User._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("user list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("user retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("user create")
        return Response({"message": "Method not allow"}, status=status.HTTP_201_CREATED)

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

        # serializer = self.get_serializer(instance, data=data, partial=partial)
        # serializer.is_valid(raise_exception=True)
        # self.perform_update(serializer)
        user = UserSerializer(instance, data=data, partial=partial)
        user.is_valid(raise_exception=True)
        user.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("user partial_update")
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
        user = UserSerializer(instance, data=data, partial=partial)
        user.is_valid(raise_exception=True)
        user.save()

        return Response(user.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("user destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response({'message': 'User deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("user soft_delete")
        instance = self.get_object()
        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'User already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()
        return Response({'detail': 'User soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_delete(self, request):
        print("user multiple_delete")
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No user IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        users = User.objects.filter(id__in=ids) 
        if not users.exists():
            return Response({'message': 'No users found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        users.update(status_enum=StatusEnum.DELETED.value)
        return Response({'message': 'Users soft deleted successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('user multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No user IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        users = User.objects.filter(id__in=ids) 
        if not users.exists():
            return Response({'message': 'No users found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        for user in users:
            user.delete()
        return Response({'message': 'Users destroy successfully'}, status=status.HTTP_200_OK)



class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminPermission]
    
    def get_queryset(self):
        first_name = self.request.query_params.get('first_name', None)
        last_name = self.request.query_params.get('last_name', None)
        username = self.request.query_params.get('username', None)
        email = self.request.query_params.get('email', None)
        phone = self.request.query_params.get('phone', None)
        gender = self.request.query_params.get('gender', None)
        address = self.request.query_params.get('address', None)
        region = self.request.query_params.get('region', None)
        company = self.request.query_params.get('company', None)
        zip_code = self.request.query_params.get('zip_code', None)
        
        type_search_first_name = self.request.query_params.get('type_search_first_name', None)
        type_search_last_name = self.request.query_params.get('type_search_last_name', None)
        type_search_username = self.request.query_params.get('type_search_username', None)
        type_search_email = self.request.query_params.get('type_search_email', None)
        type_search_phone = self.request.query_params.get('type_search_phone', None)
        type_search_gender = self.request.query_params.get('type_search_gender', None)
        type_search_address = self.request.query_params.get('type_search_address', None)
        type_search_region = self.request.query_params.get('type_search_region', None)
        type_search_company = self.request.query_params.get('type_search_company', None)
        type_search_zip_code = self.request.query_params.get('type_search_zip_code', None)
                
        queryset = User.objects.all().order_by('id')
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value)
        
        
        if first_name:
            if type_search_first_name == 'exact':
                queryset = queryset.filter(first_name=first_name)
            elif type_search_first_name == 'contains':
                queryset = queryset.filter(first_name__icontains=first_name)
            elif type_search_first_name == 'startswith':
                queryset = queryset.filter(first_name__istartswith=first_name)
            elif type_search_first_name == 'endswith':
                queryset = queryset.filter(first_name__iendswith=first_name)
            else:
                raise ValidationError("Require email type search in ['exact', 'contains', 'startswith', 'endswith]")
        if last_name:
            if type_search_last_name == 'exact':
                queryset = queryset.filter(last_name=last_name)
            elif type_search_last_name == 'contains':
                queryset = queryset.filter(last_name__icontains=last_name)
            elif type_search_last_name == 'startswith':
                queryset = queryset.filter(last_name__istartswith=last_name)
            elif type_search_last_name == 'endswith':
                queryset = queryset.filter(last_name__iendswith=last_name)
            else:
                raise ValidationError("Require email type search in ['exact', 'contains', 'startswith', 'endswith]")
        if username and type_search_username:
            if type_search_username == 'exact':
                queryset = queryset.filter(username=username)
            elif type_search_username == 'contains':
                queryset = queryset.filter(username__icontains=username)
            elif type_search_username == 'startswith':
                queryset = queryset.filter(username__istartswith=username)
            elif type_search_username == 'endswith':
                queryset = queryset.filter(username__iendswith=username)
            else:
                raise ValidationError("Require username type search in ['exact', 'contains', 'startswith', 'endswith]")
        if email and type_search_email:
            if type_search_email == 'exact':
                queryset = queryset.filter(email=email)
            elif type_search_email == 'contains':
                queryset = queryset.filter(email__icontains=email)
            elif type_search_email == 'startswith':
                queryset = queryset.filter(email__istartswith=email)
            elif type_search_email == 'endswith':
                queryset = queryset.filter(email__iendswith=email)
            else:
                raise ValidationError("Require email type search in ['exact', 'contains', 'startswith', 'endswith]")
        if phone:
            if type_search_phone == 'exact':
                queryset = queryset.filter(phone=phone)
            elif type_search_phone == 'contains':
                queryset = queryset.filter(phone__icontains=phone)
            elif type_search_phone == 'startswith':
                queryset = queryset.filter(phone__istartswith=phone)
            elif type_search_phone == 'endswith':
                queryset = queryset.filter(phone__iendswith=phone)
            else:
                raise ValidationError("Require email type search in ['exact', 'contains', 'startswith', 'endswith]")
        if gender:
            if type_search_gender == 'exact':
                queryset = queryset.filter(gender=gender)
            elif type_search_gender == 'contains':
                queryset = queryset.filter(gender__icontains=gender)
            elif type_search_gender == 'startswith':
                queryset = queryset.filter(gender__istartswith=gender)
            elif type_search_gender == 'endswith':
                queryset = queryset.filter(gender__iendswith=gender)
            else:
                raise ValidationError("Require email type search in ['exact', 'contains', 'startswith', 'endswith]")
        if address:
            if type_search_address == 'exact':
                queryset = queryset.filter(address=address)
            elif type_search_address == 'contains':
                queryset = queryset.filter(address__icontains=address)
            elif type_search_address == 'startswith':
                queryset = queryset.filter(address__istartswith=address)
            elif type_search_address == 'endswith':
                queryset = queryset.filter(address__iendswith=address)
            else: 
                raise ValidationError("Require address type search in ['exact', 'contains', 'startswith', 'endswith]")
        if region:
            if type_search_region == 'exact':
                queryset = queryset.filter(region=region)
            elif type_search_region == 'contains':
                queryset = queryset.filter(region__icontains=region)
            elif type_search_region == 'startswith':
                queryset = queryset.filter(region__istartswith=region)
            elif type_search_region == 'endswith':
                queryset = queryset.filter(region__iendswith=region)
            else: 
                raise ValidationError("Require region type search in ['exact', 'contains', 'startswith', 'endswith]")
        if company:
            if type_search_company == 'exact':
                queryset = queryset.filter(company=company)
            elif type_search_company == 'contains':
                queryset = queryset.filter(company__icontains=company)
            elif type_search_company == 'startswith':
                queryset = queryset.filter(company__istartswith=company)
            elif type_search_company == 'endswith':
                queryset = queryset.filter(company__iendswith=company)
            else: 
                raise ValidationError("Require company type search in ['exact', 'contains', 'startswith', 'endswith]")
        if zip_code:
            if type_search_zip_code == 'exact':
                queryset = queryset.filter(zip_code=zip_code)
            elif type_search_zip_code == 'contains':
                queryset = queryset.filter(zip_code__icontains=zip_code)
            elif type_search_zip_code == 'startswith':
                queryset = queryset.filter(zip_code__istartswith=zip_code)
            elif type_search_zip_code == 'endswith':
                queryset = queryset.filter(zip_code__iendswith=zip_code)
            else: 
                raise ValidationError("Require zip_code type search in ['exact', 'contains', 'startswith', 'endswith]")
        
        return queryset
    
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class UserSearchViewOR(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminPermission]
    
    def get_queryset(self):
        first_name = self.request.query_params.get('first_name', None)
        last_name = self.request.query_params.get('last_name', None)
        username = self.request.query_params.get('username', None)
        email = self.request.query_params.get('email', None)
        phone = self.request.query_params.get('phone', None)
        gender = self.request.query_params.get('gender', None)
        address = self.request.query_params.get('address', None)
        region = self.request.query_params.get('region', None)
        company = self.request.query_params.get('company', None)
        zip_code = self.request.query_params.get('zip_code', None)
        
        
        queryset = User.objects.all().order_by('id')
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value)

        filters = Q()

        
        if first_name:
            type_search_first_name = self.request.query_params.get('type_search_first_name', 'exact')
            if type_search_first_name == 'exact':
                filters |= Q(first_name=first_name)
            elif type_search_first_name == 'contains':
                filters |= Q(first_name__icontains=first_name)
            elif type_search_first_name == 'startswith':
                filters |= Q(first_name__istartswith=first_name)
            elif type_search_first_name == 'endswith':
                filters |= Q(first_name__iendswith=first_name)
            else:
                raise ValidationError("Require first name type search in ['exact', 'contains', 'startswith', 'endswith']")

        if last_name:
            type_search_last_name = self.request.query_params.get('type_search_last_name', 'exact')
            if type_search_last_name == 'exact':
                filters |= Q(last_name=last_name)
            elif type_search_last_name == 'contains':
                filters |= Q(last_name__icontains=last_name)
            elif type_search_last_name == 'startswith':
                filters |= Q(last_name__istartswith=last_name)
            elif type_search_last_name == 'endswith':
                filters |= Q(last_name__iendswith=last_name)
            else:
                raise ValidationError("Require last name type search in ['exact', 'contains', 'startswith', 'endswith']")

        if username:
            type_search_username = self.request.query_params.get('type_search_username', 'exact')
            if type_search_username == 'exact':
                filters |= Q(username=username)
            elif type_search_username == 'contains':
                filters |= Q(username__icontains=username)
            elif type_search_username == 'startswith':
                filters |= Q(username__istartswith=username)
            elif type_search_username == 'endswith':
                filters |= Q(username__iendswith=username)
            else:
                raise ValidationError("Require username type search in ['exact', 'contains', 'startswith', 'endswith']")
        
        if email:
            type_search_email = self.request.query_params.get('type_search_email', 'exact')
            if type_search_email == 'exact':
                filters |= Q(email=email)
            elif type_search_email == 'contains':
                filters |= Q(email__icontains=email)
            elif type_search_email == 'startswith':
                filters |= Q(email__istartswith=email)
            elif type_search_email == 'endswith':
                filters |= Q(email__iendswith=email)
            else:
                raise ValidationError("Require email type search in ['exact', 'contains', 'startswith', 'endswith']")
        

        if phone:
            type_search_phone = self.request.query_params.get('type_search_phone', 'exact')
            if type_search_phone == 'exact':
                filters |= Q(phone=phone)
            elif type_search_phone == 'contains':
                filters |= Q(phone__icontains=phone)
            elif type_search_phone == 'startswith':
                filters |= Q(phone__istartswith=phone)
            elif type_search_phone == 'endswith':
                filters |= Q(phone__iendswith=phone)
            else:
                raise ValidationError("Require phone type search in ['exact', 'contains', 'startswith', 'endswith']")

        if gender:
            type_search_gender = self.request.query_params.get('type_search_gender', 'exact')
            if type_search_gender == 'exact':
                filters |= Q(gender=gender)
            elif type_search_gender == 'contains':
                filters |= Q(gender__icontains=gender)
            elif type_search_gender == 'startswith':
                filters |= Q(gender__istartswith=gender)
            elif type_search_gender == 'endswith':
                filters |= Q(gender__iendswith=gender)
            else:
                raise ValidationError("Require gender type search in ['exact', 'contains', 'startswith', 'endswith']")

        if address:
            type_search_address = self.request.query_params.get('type_search_address', 'exact')
            if type_search_address == 'exact':
                filters |= Q(address=address)
            elif type_search_address == 'contains':
                filters |= Q(address__icontains=address)
            elif type_search_address == 'startswith':
                filters |= Q(address__istartswith=address)
            elif type_search_address == 'endswith':
                filters |= Q(address__iendswith=address)
            else:
                raise ValidationError("Require address type search in ['exact', 'contains', 'startswith', 'endswith']")

        if region:
            type_search_region = self.request.query_params.get('type_search_region', 'exact')
            if type_search_region == 'exact':
                filters |= Q(region=region)
            elif type_search_region == 'contains':
                filters |= Q(region__icontains=region)
            elif type_search_region == 'startswith':
                filters |= Q(region__istartswith=region)
            elif type_search_region == 'endswith':
                filters |= Q(region__iendswith=region)
            else:
                raise ValidationError("Require region type search in ['exact', 'contains', 'startswith', 'endswith']")

        if company:
            type_search_company = self.request.query_params.get('type_search_company', 'exact')
            if type_search_company == 'exact':
                filters |= Q(company=company)
            elif type_search_company == 'contains':
                filters |= Q(company__icontains=company)
            elif type_search_company == 'startswith':
                filters |= Q(company__istartswith=company)
            elif type_search_company == 'endswith':
                filters |= Q(company__iendswith=company)
            else:
                raise ValidationError("Require company type search in ['exact', 'contains', 'startswith', 'endswith']")

        if zip_code:
            type_search_zip_code = self.request.query_params.get('type_search_zip_code', 'exact')
            if type_search_zip_code == 'exact':
                filters |= Q(zip_code=zip_code)
            elif type_search_zip_code == 'contains':
                filters |= Q(zip_code__icontains=zip_code)
            elif type_search_zip_code == 'startswith':
                filters |= Q(zip_code__istartswith=zip_code)
            elif type_search_zip_code == 'endswith':
                filters |= Q(zip_code__iendswith=zip_code)
            else:
                raise ValidationError("Require zip_code type search in ['exact', 'contains', 'startswith', 'endswith']")

        
        queryset = queryset.filter(filters)

        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)