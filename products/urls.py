from . import views
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

category_list = views.CategoryViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
category_detail = views.CategoryViewSet.as_view({
    'delete': 'destroy'
})

product_list = views.ProductViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
product_detail = views.ProductViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy'
})

comment_list = views.CommentViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
comment_detail = views.CommentViewSet.as_view({
    'delete': 'destroy'
})

urlpatterns = format_suffix_patterns([
    path('products/', product_list, name='product-list'),
    path('products/<int:pk>/', product_detail, name='product-detail'),
    path('products/<int:product_pk>/comments/', comment_list, name='comment-list'),
    path('products/<int:product_pk>/comments/<int:pk>/', comment_detail, name='comment-detail'),
    path('categories/', category_list, name='category-list'),
    path('categories/<int:pk>/', category_detail, name='category-detail'),
])