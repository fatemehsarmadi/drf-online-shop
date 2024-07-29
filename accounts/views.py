from . import models
from . import serializers
from . import permissions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import RetrieveAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated

class ProfileDetail(RetrieveAPIView):
    http_method_names = ['get']
    serializer_class = serializers.ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.Profile.objects.get(user_id=self.request.user.id)
    def get_object(self):
        return self.get_queryset()
    def get(self, request, *args, **kwargs):
        try:
            profile = self.get_object()
            return super().get(request, *args, **kwargs)
        except models.Profile.DoesNotExist:
            return Response({'error': 'first, create a profile.'})

class ProfileViewSet(ListModelMixin,
                    CreateModelMixin,
                    UpdateModelMixin,
                    GenericViewSet):
    http_method_names = ['get', 'post', 'patch']
    queryset = models.Profile.objects.all()
    serializer_class = serializers.CreateUpdateProfileSerializer
    permission_classes = [permissions.CustomPermission]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context