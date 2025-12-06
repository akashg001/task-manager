from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Task


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role', 'created_at')
        read_only_fields = ('id', 'created_at')
        extra_kwargs = {
            'email': {'required': True}
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'user')
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True, 
        write_only=True,
        style={'input_type': 'password'}
    )


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model
    """
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    
    class Meta:
        model = Task
        fields = (
            'id', 
            'title', 
            'description', 
            'completed', 
            'created_at', 
            'updated_at',
            'owner',
            'owner_username'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'owner')
    
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating tasks
    """
    class Meta:
        model = Task
        fields = ('title', 'description', 'completed')
        extra_kwargs = {
            'description': {'required': False},
            'completed': {'required': False}
        }