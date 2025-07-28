from rest_framework import viewsets
from .models import Cart, Product, UserAccount, Group, CartProduct, Category
from .serializers import CartSerializer, ProductSerializer, UserRegisterSerializer, UserLoginSerializer, UserSerializer, GroupSerializer, CategorySerializer
# from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, login, logout
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from rest_framework.decorators import action


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
    permission_classes = [IsAuthenticated]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(members=self.request.user)

    def perform_create(self, serializer):
        group = serializer.save(creator=self.request.user)
        group.members.add(self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def leave(self, request, pk=None):
        group = self.get_object()
        user = request.user
        if user == group.creator:
            return Response({"detail": "El creador no puede abandonar el grupo"}, status=400)
        group.members.remove(user)
        return Response({"detail": "Has salido del grupo"}, status=200)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def invite(self, request, pk=None):
        group = self.get_object()
        user_ids = request.data.get('user_ids', [])
        users = UserAccount.objects.filter(id__in=user_ids)
        group.members.add(*users)
        return Response({"detail": "Usuarios invitados correctamente"}, status=200)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def generate_cart(self, request, pk=None):
        group = self.get_object()

        if request.user not in group.members.all():
            return Response({"detail": "No tienes permiso"}, status=403)

        # Create or reset the cart
        Cart.objects.filter(group=group).delete()
        cart = Cart.objects.create(group=group)

        # Dummy logic: add some products
        sample_products = Product.objects.all()[:5]
        for product in sample_products:
            CartProduct.objects.create(cart=cart, product=product, quantity=1)

        return Response({"detail": "Carrito generado automáticamente"}, status=200)