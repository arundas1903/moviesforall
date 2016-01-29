from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import AppUser


class UserSerializer(serializers.Serializer):

    """
        User model serializer
    """

    username = serializers.CharField(max_length=100, validators=[UniqueValidator(
        queryset=AppUser.objects.all())])
    password = serializers.CharField(max_length=100)
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=30, required=False)
    email = serializers.EmailField(max_length=100, validators=[UniqueValidator(
        queryset=AppUser.objects.all())])
    is_staff = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    is_subscribed = serializers.BooleanField(required=False)

    def create(self, validated_data):
        user = AppUser.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        # If not data save old data
        instance.username = validated_data.get('username', instance.username)
        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.is_subscribed = validated_data.get('is_subscribed', instance.is_subscribed)
        instance.save()
        return instance
