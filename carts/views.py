from . import models
from . import serializers
from . import permissions
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, DestroyModelMixin, UpdateModelMixin

class CartViewSet(ListModelMixin,
                RetrieveModelMixin,
                CreateModelMixin,
                DestroyModelMixin,
                GenericViewSet):
    queryset = models.Cart.objects.all()
    serializer_class = serializers.CartSerializer
    permission_classes = [permissions.IsSelf]

    def get_queryset(self):
        return models.Cart.objects.filter(user_id=self.request.user.id)

    def get_serializer_context(self):
        return {'request': self.request}

class CartItemViewSet(RetrieveModelMixin,
                    CreateModelMixin,
                    UpdateModelMixin,
                    DestroyModelMixin,
                    GenericViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    def get_queryset(self):
        try:
            cart = models.Cart.objects.select_related('user').get(id=self.kwargs['cart_pk'], user_id=self.request.user.id)
            return models.CartItem.objects.filter(cart_id=self.kwargs['cart_pk'])
        except models.Cart.DoesNotExist:
            return []
    def get_serializer_class(self):
        if self.request.method in ('GET', 'POST'):
            return serializers.CreateCartItemSerializer
        else:
            return serializers.UpdateDeleteCartItemSerializer
    def get_serializer_context(self):
        context = {}
        if 'pk' in self.kwargs:
            context['pk'] = self.kwargs['pk']
        context['cart_id'] = self.kwargs['cart_pk']
        context['request'] = self.request
        return context