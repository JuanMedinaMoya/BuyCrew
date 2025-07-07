from django.forms import ValidationError
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from .models import Cart, Product, UserAccount
from django.contrib.auth import get_user_model, authenticate

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserAccount
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = UserAccount(**validated_data)
        user.set_password(password)
        user.save()

        return user
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(username=email, password=password)
        
        if not user:
            raise AuthenticationFailed('Invalid email or password')

        if not user.is_active:
            raise AuthenticationFailed('User is inactive')

        data['user'] = user
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['email', 'name']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

