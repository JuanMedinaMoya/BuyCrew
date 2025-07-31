from django.forms import ValidationError
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from .models import Cart, Product, UserAccount, Group, Category
from django.contrib.auth import get_user_model, authenticate

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserAccount
        exclude = ['groups', 'user_permissions', 'is_active']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = UserAccount.objects.create_user(password=password, **validated_data)
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
    estimated_weight_per_unit = serializers.SerializerMethodField()
    estimated_total_weight = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "price", "stock", "categories",
            "weight_kg", "units", "weight_per_unit_kg", "description",
            "estimated_weight_per_unit", "estimated_total_weight"
        ]

    def get_estimated_weight_per_unit(self, obj):
        return obj.estimated_weight_per_unit

    def get_estimated_total_weight(self, obj):
        return obj.estimated_total_weight


class GroupSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=UserAccount.objects.all()
    )
    class Meta:
        model = Group
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'parent']
