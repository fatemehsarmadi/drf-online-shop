from . import models
from django.db.models import Avg
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework.reverse import reverse
from rest_framework import serializers

class RetrieveProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['id', 'title', 'category', 'price', 'inventory', 'rating']

    category = serializers.StringRelatedField()

class CreateUpdateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['title', 'category_id', 'price', 'inventory']
    category_id = serializers.IntegerField()

    def validate_title(self, value):
        length_of_title = len(str(value))
        if length_of_title < 3:
            raise serializers.ValidationError('minimum title length: 3')
        return value

    def validate_category_id(self, value):
        try:
            category = models.Category.objects.get(pk=value)
            return value
        except models.Category.DoesNotExist:
            raise serializers.ValidationError('this category does not already exist')

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError('price cannot be negative')
        return value
    
    def validate_inventory(self, value):
        if value < 0:
            raise serializers.ValidationError('inventory cannot be negative')
        return value
    
    def save(self, **kwargs):
        if self.instance: #update
            old_instance = models.Product.objects.get(pk=self.instance.id)
            product = super().save(**kwargs)
            if old_instance.price != self.validated_data['price']:
                models.ProductHistory.objects.create(
                    product=product,
                    change_type='price updated',
                    description=f"price changed from {old_instance.price} to {self.validated_data['price']}."
                )
            if old_instance.inventory != self.validated_data['inventory']:
                models.ProductHistory.objects.create(
                    product=product,
                    change_type='inventory updated',
                    description=f"inventory changed from {old_instance.inventory} to {self.validated_data['inventory']}."
                )
        else: #create
            product = super().save(**kwargs)
            models.ProductHistory.objects.create(
                product=product,
                change_type='created',
                description=f'product {product.title} was created with initial inventory {product.inventory}.'
            )
        return product

class SimpleUserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'first_name', 'last_name']

class RetrieveCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = ['description', 'rating', 'date', 'user']

    user = SimpleUserSerializer()

class AddCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = ['rating', 'description']

    def validate(self, attrs):
        product_id = self.context['product_id']
        user_id = self.context['request'].user.id
        try:
            product = models.Product.objects.get(pk=product_id)
            comment = models.Comment.objects.get(user_id=user_id, product_id=product_id)
        except models.Product.DoesNotExist:
            raise serializers.ValidationError('this product does not exist')
        except models.Comment.DoesNotExist:
            return attrs
        raise serializers.ValidationError('you have already registered a comment for this product!')

    def validate_rating(self, value):
        if value < 0:
            raise serializers.ValidationError('rating cannot be negative')
        elif value > 5:
            raise serializers.ValidationError('maximum valid value for rating: 5.0')
        return value

    def create(self, validated_data):
        product_id = self.context['product_id']
        user_id = self.context['request'].user.id
        comment = models.Comment.objects.create(user_id=user_id, product_id=product_id, **self.validated_data)
        product = comment.product

        total_rating = models.Comment.objects.select_related('product').filter(product_id=product_id).aggregate(rating=Avg('rating'))['rating']
        product.rating = total_rating
        product.save()

        return comment

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['id', 'name', 'description', 'products']

    products = serializers.SerializerMethodField(method_name='get_products_link')

    def get_products_link(self, category):
        request = self.context['request']
        return reverse('product-list', request=request) + f'?category={category.id}' 

    def validate_name(self, value):
        if models.Category.objects.filter(name=value):
            raise serializers.ValidationError('a category with this name has already been added')
        length_of_name = len(str(value))
        if length_of_name < 3:
            raise serializers.ValidationError('minimum title length: 3')
        return value