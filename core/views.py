from rest_framework import viewsets
from .models import Cart, Product, UserAccount
from .serializers import CartSerializer, ProductSerializer, UserRegisterSerializer, UserLoginSerializer, UserSerializer
# from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, login, logout
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render

class CreateUserView(generics.CreateAPIView):
    queryset = UserAccount.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

class UserRegister(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        # validated_data = custom_validation(request.data)
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(request.data)
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class UserLogin(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'email': user.email,
                'name': user.name,
            }
        }, status=status.HTTP_200_OK)

class UserLogout(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)
        
class UserView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    def get(self, request):
        # validated_data = custom_validation(request.data)
        serializer = UserSerializer(request.user)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
