from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    slug = models.SlugField(null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='products', null=True)
    price = models.DecimalField(max_digits=10, decimal_places=1)
    inventory = models.PositiveIntegerField()
    rating = models.FloatField(null=True, default=0)

class ProductHistory(models.Model):
    change_type = models.CharField(max_length=50)
    change_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='history')

    def __str__(self):
        return f'history for {self.product} - {self.change_type}'

class Comment(models.Model):
    description = models.TextField(null=True)
    rating = models.FloatField()
    date = models.DateTimeField(auto_now=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE ,related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    class Meta:
        unique_together = [['user', 'product']]