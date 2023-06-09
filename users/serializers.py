from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from rest_framework import serializers
import dj_rest_auth.serializers


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name',)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class UserSerializer(dj_rest_auth.serializers.UserDetailsSerializer):
    class Meta:
        model = get_user_model()
        exclude = ('user_permissions', 'is_staff', 'is_superuser', 'last_login', 'client', 'password',)
        read_only_fields = ('email', 'date_joined', 'is_active')


class SearchUsersResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'name', 'email', 'avatar')
        read_only_fields = ('id', 'name', 'email', 'avatar')
