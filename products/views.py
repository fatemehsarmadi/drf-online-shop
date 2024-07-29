from . import models
from . import serializers
from . import permissions
from statistics import mean
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin

class ProductViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = models.Product.objects.select_related('category').all()
    permission_classes = [permissions.IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.RetrieveProductSerializer
        return serializers.CreateUpdateProductSerializer
    def create(self, request, *args, **kwargs):
        serializer = serializers.CreateUpdateProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        serializer = serializers.RetrieveProductSerializer(product)
        return Response(serializer.data)

class CommentViewSet(ListModelMixin,
                    CreateModelMixin,
                    DestroyModelMixin,
                    GenericViewSet):
    http_method_names = ['get', 'post', 'delete']
    permission_classes = [permissions.IsOwnerOrIsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return models.Comment.objects.none()
        return models.Comment.objects.filter(product_id=self.kwargs['product_pk'])
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.RetrieveCommentSerializer
        return serializers.AddCommentSerializer    

    def get_serializer_context(self):
        return {'request': self.request, 'product_id': self.kwargs['product_pk']}

    def destroy(self, request, *args, **kwargs):
        user_id = request.user.id
        product_id = self.kwargs['product_pk']
        try:
            ratings = models.Comment.objects.select_related('product')\
            .filter(product_id=product_id)\
            .exclude(user_id=user_id)\
            .values_list('rating', flat=True)
            product = models.Product.objects.get(pk=product_id)
            product.rating = mean(ratings)
            product.save()
        except models.Comment.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

class CategoryViewSet(ListModelMixin,
                    CreateModelMixin,
                    DestroyModelMixin,
                    GenericViewSet):
    http_method_names = ['get', 'post', 'delete']
    permission_classes = [permissions.IsAdminOrReadOnly]
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer

    def get_serializer_context(self):
        return {'request': self.request}