from carts import models
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

@receiver(post_save, sender=models.CartItem)
def decrease_product_inventory(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        product.inventory -= instance.quantity
        product.save()

@receiver(pre_delete, sender=models.CartItem)
def increase_product_inventory(sender, instance, **kwargs):
    product = instance.product
    product.inventory += instance.quantity
    product.save()