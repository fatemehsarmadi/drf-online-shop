from . import models
from datetime import datetime
from django.db import transaction
from rest_framework import serializers

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ['product', 'quantity', 'unit_price', 'price']
    unit_price = serializers.SerializerMethodField(method_name='get_unit_price')
    price = serializers.SerializerMethodField(method_name='get_price')

    def get_unit_price(self, item: models.CartItem):
        return item.product.price
    def get_price(self, item: models.CartItem):
        return item.quantity * item.product.price

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = ['id', 'updated_at', 'items', 'total_price']
    items = ItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    def get_total_price(self, cart: models.Cart):
        return sum([item.quantity * item.product.price for item in cart.items.all()])
    
    def validate(self, attrs):
        user_id = self.context['request'].user.id
        if models.Cart.objects.filter(user_id=user_id).count() >= 2:
            raise serializers.ValidationError('creating more than 2 shopping carts is not allowed')
        return attrs

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        cart = models.Cart.objects.create(user_id=user_id, **validated_data)
        return cart

class CreateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ['quantity', 'product', 'cart_id']

    cart_id = serializers.IntegerField(read_only=True)
    product = serializers.HyperlinkedRelatedField(view_name='product-detail', queryset=models.Product.objects.all())

    def validate_product_id(self, value):
        if not models.Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('no product with the given id was found')
        return value
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('quantity must be greater than zero')
        return value

    @transaction.atomic
    def create(self, validated_data):
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        cart_id = self.context['cart_id']
        self.validated_data['cart_id'] = cart_id
        product = models.Product.objects.get(pk=product_id)
        
        if quantity > product.inventory:
            raise serializers.ValidationError('this item is not in stock')
        
        try:
            item = models.CartItem.objects.get(product_id=product_id, cart_id=cart_id)
            raise serializers.ValidationError('this item has already been added. use PATCH method to edit the quantity')
        except models.CartItem.DoesNotExist:
            cart = models.Cart.objects.get(id=cart_id)
            cart.updated_at = datetime.now()
            cart.save()
            return super().create(validated_data)

    @transaction.atomic
    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        product = models.Product.objects.get(pk=product_id)
        
        if self.instance: #update
            item = models.CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            if (quantity - item.quantity) > product.inventory:
                raise serializers.ValidationError('this item is not in stock')
            item.quantity += quantity
            item.save()
            self.instance = item
        else: # create
            if quantity > product.inventory:
                raise serializers.ValidationError('this item is not in stock')
            kwargs['cart_id'] = cart_id
            super().save(**kwargs)
        
        cart = models.Cart.objects.get(id=cart_id)
        cart.updated_at = datetime.now()
        cart.save()
        return self.instance

class UpdateDeleteCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ['quantity']

    def validate(self, attrs):
        item_id = self.context['pk']
        item = models.CartItem.objects.select_related('product').get(pk=item_id)
        product = item.product
        quantity = attrs['quantity']

        if (quantity - item.quantity) > product.inventory:
            raise serializers.ValidationError('this item is not in stock')
        return attrs

    def validate_product_id(self, value):
        if not models.Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('no product with the given id was found')
        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('quantity must be greater than zero')
        return value

    @transaction.atomic
    def save(self, **kwargs):
        item_id = self.context['pk']
        item = models.CartItem.objects.select_related('product').get(pk=item_id)
        product = item.product
        quantity = self.validated_data['quantity']

        if (quantity - item.quantity) > product.inventory:
            raise serializers.ValidationError('this item is not in stock')
        
        diff = item.quantity - quantity
        item.quantity = quantity
        item.save()
        product.inventory += diff
        product.save()

        cart = models.Cart.objects.get(id=self.context['cart_id'])
        cart.updated_at = datetime.now()
        cart.save()
        return super().save(**kwargs)