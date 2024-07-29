from . import views
from django.urls import path

profile_list = views.ProfileViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
product_detail = views.ProfileViewSet.as_view({
    'patch': 'partial_update'
})

urlpatterns = [
    path('profiles/me/', views.ProfileDetail.as_view()),
    path('profiles/', profile_list, name='profile-list'),
    path('profiles/<int:pk>/', product_detail, name='profile-detail'),
]