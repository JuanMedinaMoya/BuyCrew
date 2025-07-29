from rest_framework import viewsets
from .models import Cart, Product, UserAccount, Group, CartProduct, Category, EventType
from .serializers import CartSerializer, ProductSerializer, UserRegisterSerializer, UserLoginSerializer, UserSerializer, GroupSerializer, CategorySerializer, EventTypeSerializer
# from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, login, logout, authenticate, login
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import action
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.template.context_processors import csrf
from django.shortcuts import get_list_or_404

class CreateUserView(generics.CreateAPIView):
    queryset = UserAccount.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

class UserRegister(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            response = HttpResponse()
            response['HX-Redirect'] = '/'
            return response
        return Response(serializer.errors, status=400)

class UserLogin(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        login(request, user)

        response = HttpResponse()
        response['HX-Redirect'] = '/'
        return response

class UserLogout(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        logout(request)
        response = HttpResponse()
        response['HX-Redirect'] = '/'
        return response
        


class UserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        context = {'user': request.user}
        context.update(csrf(request))

        if request.user.is_authenticated:
            html = render_to_string("core/navbar_authenticated.html", context)
        else:
            html = render_to_string("core/navbar_anonymous.html")
        return HttpResponse(html)


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
    

class EventTypeViewSet(viewsets.ModelViewSet):
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer
    permission_classes = [IsAuthenticated]

def login_view(request):
    return render(request, "core/login.html")

def register_view(request):
    return render(request, "core/register.html")

def home_view(request):
    models = ['product', 'category', 'group', 'event_type']
    return render(request, "core/home.html", {"models": models})

def product_create_view(request):
    categories = Category.objects.all()
    return render(request, "core/product_form.html", {"category_list": categories})

def product_list_view(request):
    items = Product.objects.all()
    return render(request, "core/product_list.html", {"items": items})

def category_create_view(request):
    return render(request, "core/category_form.html")

def category_list_view(request):
    items = Category.objects.all()
    return render(request, "core/category_list.html", {"items": items})

def group_create_view(request):
    return render(request, "core/group_form.html")

def group_list_view(request):
    items = Group.objects.all()
    return render(request, "core/group_list.html", {"items": items})

def event_type_create_view(request):
    return render(request, "core/event_type_form.html")

def event_type_list_view(request):
    items = EventType.objects.all()
    return render(request, "core/event_type_list.html", {"items": items})
