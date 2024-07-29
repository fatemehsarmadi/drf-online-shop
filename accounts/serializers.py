from . import models
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['username', 'email', 'password',
                'first_name', 'last_name']

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['username', 'email',
                'first_name', 'last_name']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = ['city', 'address', 'street_number',
                'zip_code', 'user_id']

class CreateUpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = ['occupation', 'city', 'address', 'street_number',
                'flat_number', 'zip_code', 'user_id']

    def create(self, validated_data):
        validated_data['user_id'] = self.context['request'].user.id
        return super().create(validated_data)
    def update(self, instance, validated_data):
        validated_data['user_id'] = self.context['request'].user.id
        return super().update(instance, validated_data)