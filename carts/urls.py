from . import views
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

cart_list = views.CartViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
cart_detail = views.CartViewSet.as_view({
    'get': 'retrieve',
    'delete': 'destroy'
})
item_list = views.CartItemViewSet.as_view({
    'post': 'create'
})
item_detail = views.CartItemViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = format_suffix_patterns([
    path('carts/', cart_list, name='cart-list'),
    path('carts/<int:pk>/', cart_detail, name='cart-detail'),
    path('carts/<int:cart_pk>/items/', item_list, name='item-list'),
    path('carts/<int:cart_pk>/items/<int:pk>/', item_detail, name='item-detail'),
])