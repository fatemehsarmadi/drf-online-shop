from django.db import models
from django.conf import settings
from products.models import Product

class Cart(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')

class CartItem(models.Model):
    quantity = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cartitems')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    
    class Meta:
        unique_together = [['product', 'cart'],]