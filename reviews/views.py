from django.db.models import Q
from rest_framework.response import Response
from rest_framework import viewsets, generics, status
from rest_framework.exceptions import ValidationError
from reviews.serializers import ReviewSerializer, ReviewSerializerOutput, ReviewUpdateSerializer, IdsReviewSerializer
from app.serializers import ResponseSerializer
from reviews.models import Review, StatusEnum
from products.models import SubProduct
from rest_framework.decorators import action
from authentication.permissions import IsCustomerPermission, IsAdminPermission, IsAuthenticatedPermission
from drf_yasg.utils import swagger_auto_schema

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by('id')
    serializer_class = ReviewSerializer
    
    def get_authenticators(self):
        print("get_authenticators")
        if getattr(self, 'action', None) in ['list', 'retrieve']:
            return []
        return super().get_authenticators()


    def get_permissions(self):
        print("get_permissions")
        print(self.action)
        if self.action in ['create', 'update', 'partial_update', 'soft_delete', 'destroy', 'multiple_delete', 'multiple_destroy', 'my_cart']: 
            return [(IsCustomerPermission)()]
        elif self.action in ['list', 'retrieve']:
            return [] 
        return [IsAdminPermission()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ReviewUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return ReviewSerializer
        elif self.action in ['multiple_delete', 'multiple_destroy']:
            return IdsReviewSerializer
        return ReviewSerializer

    # loc dau vao cua cac phuong thuc get
    def get_queryset(self):
        queryset = self.queryset            
        params = self.request.query_params

        filter_kwargs = {}

        for param, value in params.items():
            if param in [field.name for field in Review._meta.get_fields()]:
                filter_kwargs[param] = value
        queryset = queryset.filter(status_enum=StatusEnum.ACTIVE.value, **filter_kwargs)
        return queryset

    #read all
    def list(self, request, *args, **kwargs):
    # def custom_list(self, request):
        print("review list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ReviewSerializerOutput(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ReviewSerializerOutput(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def retrieve(self, request, *args, **kwargs):
        print("review retrieve")
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=ReviewUpdateSerializer,
        responses={200: ResponseSerializer}
    )
    def create(self, request, *args, **kwargs):
        print("review create")
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
        review = ReviewSerializer(data=data)
        if review.is_valid():
            review.save()
        else:
            return Response(
                {"detail": "Review is invalid",  "errors": review.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"review": review.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if user_id != instance.user.id: 
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        review = ReviewSerializer(instance, data=data, partial=partial)
        review.is_valid(raise_exception=True)
        review.save()

        reviewModel = Review.objects.get(id=review.data.get('id'))

        reviewOutput = ReviewSerializerOutput(reviewModel)
    
        return Response(reviewOutput.data, status=status.HTTP_200_OK)


    def partial_update(self, request, *args, **kwargs):
        print("review partial_update")
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()

        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        sub_product_id = request.data.get('sub_product_id', None)
        if sub_product_id != None:
            return Response({'detail': 'SubProduct cannot be updated'}, status=status.HTTP_403_FORBIDDEN)
        
        review = ReviewSerializer(instance, data=data, partial=partial)
        review.is_valid(raise_exception=True)
        review.save()

        reviewModel = Review.objects.get(id=review.data.get('id'))

        reviewOutput = ReviewSerializerOutput(reviewModel)
    
        return Response(reviewOutput.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def destroy(self, request, *args, **kwargs):
        print("review destroy")
        pk = request.parser_context['kwargs'].get('pk')
        try:
            instance = Review.objects.get(id=pk)
        except Review.DoesNotExist:
            return Response({'detail': 'Review not found'}, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)
        
        instance.delete()
        return Response({'message': 'Review deleted successfully!'}, status=status.HTTP_200_OK)

    # soft delete
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        print("review soft_delete")
        instance = self.get_object()

        user_id = request.user.id
        if user_id != instance.user.id:
            return Response({
                "detail": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        if instance.status_enum == StatusEnum.DELETED.value:
            return Response({'detail': 'Review already soft deleted'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status_enum = StatusEnum.DELETED.value
        instance.save()
        return Response({'detail': 'Review soft deleted successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='multiple-delete')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_delete(self, request):
        print("review multiple_delete")

        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No review IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        reviews = Review.objects.filter(id__in=ids) 
        if not reviews.exists():
            return Response({'message': 'No reviews found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for instance in reviews: 
            if user_id != instance.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)

        reviews.update(status_enum=StatusEnum.DELETED.value)
        return Response({'message': 'Reviews soft deleted successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['post'], url_path='multiple-destroy')
    @swagger_auto_schema(
        responses={200: ResponseSerializer}
    )
    def multiple_destroy(self, request):
        print('review multiple_destroy')
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No review IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        reviews = Review.objects.filter(id__in=ids) 
        if not reviews.exists():
            return Response({'message': 'No reviews found with the provided IDs'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        for review in reviews:
            if user_id != review.user.id:
                return Response({
                    "detail": "You do not have permission to perform this action."
                }, status=status.HTTP_403_FORBIDDEN)
            review.delete()

        return Response({'message': 'Reviews destroy successfully'}, status=status.HTTP_200_OK)
    
    # multiple destroy
    @action(detail=False, methods=['get'], url_path='my-cart')
    @swagger_auto_schema(
        responses={200: ReviewSerializerOutput}
    )
    def my_cart(self, request):
        print('review my_cart')

        user_id = request.user.id
        # print("user_id", user_id)
        # try:
        #     reviews = self.queryset.filter(user=user_id)
        # except Review.DoesNotExist: 
        #     return Response({'detail': 'No item found in my cart'}, status=status.HTTP_403_FORBIDDEN) 
        reviews = self.queryset.filter(user=user_id, status_enum=StatusEnum.ACTIVE.value)

        if not reviews.exists():
            return Response({'detail': 'No item found in my cart'}, status=status.HTTP_404_NOT_FOUND)

        # print("reviews", reviews)
        reviewOutput = ReviewSerializerOutput(reviews, many=True)

        return Response(reviewOutput.data, status=status.HTTP_200_OK)

