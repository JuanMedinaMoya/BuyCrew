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
from django.shortcuts import redirect, render
from rest_framework.decorators import action
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import get_list_or_404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

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

@csrf_protect
def product_create_view(request):
    context = {"category_list": Category.objects.all()}

    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        ratio = request.POST.get("ratio_consumo")
        categories = request.POST.getlist("categories")

        if not categories:
            context["error"] = "Debes seleccionar al menos una categoría."
        else:
            product = Product.objects.create(
                name=name,
                price=price,
                stock=stock,
                ratio_consumo=ratio
            )
            product.categories.set(categories)
            context["success"] = "✅ Producto creado correctamente"

    return render(request, "core/product_form.html", context)



def product_list_view(request):
    items = Product.objects.all()
    return render(request, "core/product_list.html", {"items": items})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "core/product_detail.html", {"product": product})



@require_POST
@csrf_protect
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect("/product/list/?deleted=1")

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

@csrf_protect
def category_create_view(request):
    context = {"category_list": Category.objects.all()}

    if request.method == "POST":
        name = request.POST.get("name")
        parent_name = request.POST.get("parent")
        parent = Category.objects.filter(name=parent_name).first() if parent_name else None

        if Category.objects.filter(name=name).exists():
            context["error"] = f"La categoría '{name}' ya existe."
        else:
            Category.objects.create(name=name, parent=parent)
            context["success"] = f"✅ Categoría '{name}' creada correctamente"
    
    return render(request, "core/category_form.html", context)


def category_list_view(request):
    items = Category.objects.all()
    return render(request, "core/category_list.html", {"items": items})

@csrf_protect
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")
        product.ratio_consumo = request.POST.get("ratio_consumo")

        category_ids = request.POST.getlist("categories")
        product.save()
        product.categories.set(category_ids)

        response = HttpResponse()
        response['HX-Redirect'] = f'/product/{product.pk}/?updated=1'
        return response

    return render(request, "core/product_form.html", {
        "product": product,
        "category_list": categories,
        "edit_mode": True
    })

def category_detail_view(request, name):
    category = get_object_or_404(Category, name=name)
    return render(request, "core/category_detail.html", {"category": category})


@csrf_protect
def category_edit_view(request, name):
    category = get_object_or_404(Category, name=name)
    categories = Category.objects.exclude(name=category.name)

    context = {
        "category_list": categories,
        "edit_mode": True,
        "category": category
    }

    if request.method == "POST":
        # name = request.POST.get("name")  ← ya no usamos esto
        parent_name = request.POST.get("parent")
        parent = Category.objects.filter(name=parent_name).first() if parent_name else None

        category.parent = parent
        category.save()

        response = HttpResponse()
        response['HX-Redirect'] = f"/category/{category.name}/?updated=1"
        return response

    return render(request, "core/category_form.html", context)

@require_POST
@csrf_protect
def category_delete_view(request, name):
    category = get_object_or_404(Category, name=name)
    category.delete()
    return redirect("/category/list/?deleted=1")
