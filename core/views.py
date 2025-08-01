import json
from rest_framework import viewsets
from .models import Cart, Product, UserAccount, Group, CartProduct, Category, Order, OrderItem
from .serializers import CartSerializer, ProductSerializer, UserRegisterSerializer, UserLoginSerializer, UserSerializer, GroupSerializer, CategorySerializer
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
from django.http import HttpResponse, HttpResponseForbidden
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import get_list_or_404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from .utils.ai_cart_generator import generate_cart_with_gpt

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
            carritos_por_grupo = []
            for group in request.user.groups_in.all():
                carrito = group.carts.filter(active=True).first()
                if carrito:
                    carritos_por_grupo.append((group.name, carrito.id, carrito.pk))
            context['carritos_por_grupo'] = carritos_por_grupo

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
    

def login_view(request):
    return render(request, "core/login.html")

def register_view(request):
    return render(request, "core/register.html")

def home_view(request):
    models = ['product', 'category', 'group']
    carritos_por_grupo = []

    if request.user.is_authenticated:
        for group in request.user.groups_in.all():
            carrito = group.carts.filter(active=True).first()
            if carrito:
                carritos_por_grupo.append((group.name, carrito.id, carrito.pk))

    return render(request, "core/home.html", {
        "models": models,
        "carritos_por_grupo": carritos_por_grupo,
    })


@csrf_protect
def product_create_view(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Solo los administradores pueden realizar esta acción.")
    context = {"category_list": Category.objects.all()}

    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        description = request.POST.get("description") or ""
        weight_kg = request.POST.get("weight_kg") or None
        units = request.POST.get("units") or None
        weight_per_unit_kg = request.POST.get("weight_per_unit_kg") or None
        categories = request.POST.getlist("categories")
        image = request.FILES.get("image")

        weight_kg = float(weight_kg) if weight_kg else None
        units = int(units) if units else None
        weight_per_unit_kg = float(weight_per_unit_kg) if weight_per_unit_kg else None

        product = Product.objects.create(
            name=name,
            price=price,
            stock=stock,
            description=description,
            weight_kg=weight_kg or None,
            units=units or None,
            weight_per_unit_kg=weight_per_unit_kg or None,
            image=image
        )
        product.categories.set(categories)
        context["success"] = "✅ Producto creado correctamente"

    return render(request, "core/product_form.html", context)



def product_list_view(request):
    search = request.GET.get("search", "")
    items = Product.objects.all()
    if search:
        items = items.filter(name__icontains=search)

    if request.headers.get("HX-Request") == "true":
        return render(request, "core/fragments/product_table.html", {"items": items})

    return render(request, "core/product_list.html", {"items": items})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "core/product_detail.html", {"product": product})

def product_detail_card(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "core/fragments/product_detail_card.html", {"product": product})

@require_POST
@csrf_protect
def product_delete(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden("Solo los administradores pueden realizar esta acción.")
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect("/product/list/?deleted=1")


@csrf_protect
def group_create_view(request):

    if not request.user.is_authenticated:
        return redirect('login')

    context = {}

    if request.method == "POST":
        name = request.POST.get("name")
        people_count = request.POST.get("people_count")
        duration_days = request.POST.get("duration_days")
        preferences = request.POST.get("preferences")
        restrictions = request.POST.get("restrictions")
        high_consume = bool(request.POST.get("high_consume"))
        description = request.POST.get("description", "")

        group = Group.objects.create(
            name=name,
            creator=request.user,
            people_count=people_count,
            duration_days=duration_days,
            preferences=preferences,
            restrictions=restrictions,
            high_consume=high_consume,
            description=description
        )
        group.members.add(request.user)
        context["success"] = "✅ Grupo creado correctamente"

    return render(request, "core/group_form.html", context)

def group_list_view(request):
    if request.user.is_staff:
        search_query = request.GET.get("search", "").strip()
        all_groups = Group.objects.all()
        if search_query:
            all_groups = all_groups.filter(name__icontains=search_query)
    else:
        all_groups = Group.objects.filter(members=request.user)

    creador_groups = all_groups.filter(creator=request.user)
    miembro_groups = all_groups.exclude(creator=request.user)

    grupos_con_carrito = set()
    for group in all_groups:
        if group.carts.filter(active=True).exists():
            grupos_con_carrito.add(group.pk)

    if request.headers.get("HX-Request") and request.user.is_staff:
        return render(request, "core/fragments/group_table_fragment.html", {
            "all_groups": all_groups,
            "grupos_con_carrito": grupos_con_carrito,
        })

    return render(request, "core/group_list.html", {
        "creador_groups": creador_groups,
        "miembro_groups": miembro_groups,
        "grupos_con_carrito": grupos_con_carrito,
        "all_groups": all_groups if request.user.is_staff else None
    })


@csrf_protect
def group_detail_view(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if not request.user.is_staff and request.user not in group.members.all():
        return HttpResponseForbidden("No tienes acceso a este grupo.")

    all_users = UserAccount.objects.exclude(id=request.user.id)
    active_cart = group.carts.filter(active=True).first()
    past_carts = group.carts.filter(active=False).order_by('-id')
    past_orders = Order.objects.filter(group=group).order_by('-created_at')

    return render(request, "core/group_detail.html", {
        "group": group,
        "all_users": all_users,
        "active_cart": active_cart,
        "past_carts": past_carts,
        "past_orders": past_orders
    })

@csrf_protect
def group_edit_view(request, pk):
    group = get_object_or_404(Group, pk=pk)

    if request.user != group.creator and not request.user.is_staff:
        return HttpResponseForbidden("Solo el creador o un administrador puede editar este grupo.")
    if request.method == "POST":
        group.name = request.POST.get("name")
        group.people_count = request.POST.get("people_count")
        group.duration_days = request.POST.get("duration_days")
        group.preferences = request.POST.get("preferences")
        group.restrictions = request.POST.get("restrictions")
        group.high_consume = bool(request.POST.get("high_consume"))
        group.description = request.POST.get("description", "")

        group.save()

        response = HttpResponse()
        response['HX-Redirect'] = f'/group/{group.pk}/?updated=1'
        return redirect('group_detail', pk=group.pk)

    return render(request, "core/group_form.html", {
        "group": group,
        "edit_mode": True
    })

@csrf_protect
def group_join_view(request):
    context = {}
    if request.method == "POST":
        code = request.POST.get("invite_code", "").strip().upper()
        group = Group.objects.filter(invite_code=code).first()

        if not group:
            context["error"] = "❌ Código inválido."
        elif request.user in group.members.all():
            context["error"] = "⚠️ Ya formas parte de este grupo."
        else:
            group.members.add(request.user)
            context["success"] = f"✅ Te has unido a '{group.name}' correctamente."

    return render(request, "core/group_join.html", context)


@require_POST
@csrf_protect
def group_delete_view(request, pk):
    group = get_object_or_404(Group, pk=pk)
    group.delete()
    return redirect("/group/list/?deleted=1")

@csrf_protect
def category_create_view(request):

    if not request.user.is_staff:
        return HttpResponseForbidden("Solo los administradores pueden modificar categorías.")

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
    query = request.GET.get("search", "")
    categories = Category.objects.all()
    if query:
        categories = categories.filter(name__icontains=query)

    context = {
        "items": categories
    }

    if request.headers.get("HX-Request"):
        return render(request, "core/fragments/category_table.html", context)

    return render(request, "core/category_list.html", context)


@csrf_protect
def product_edit(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden("Solo los administradores pueden realizar esta acción.")
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")
        product.description = request.POST.get("description")
        image = request.FILES.get("image")
        if image:
            product.image = image

        # Conversión segura a float/int si están presentes
        weight_kg = request.POST.get("weight_kg")
        units = request.POST.get("units")
        weight_per_unit_kg = request.POST.get("weight_per_unit_kg")

        product.weight_kg = float(weight_kg) if weight_kg else None
        product.units = int(units) if units else None
        product.weight_per_unit_kg = float(weight_per_unit_kg) if weight_per_unit_kg else None

        product.save()

        category_ids = request.POST.getlist("categories")
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
    if not request.user.is_staff:
        return HttpResponseForbidden("Solo los administradores pueden modificar categorías.")

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
    if not request.user.is_staff:
        return HttpResponseForbidden("Solo los administradores pueden modificar categorías.")

    category = get_object_or_404(Category, name=name)
    category.delete()
    return redirect("/category/list/?deleted=1")

@csrf_protect
def cart_create_view(request, group_id):
    group = get_object_or_404(Group, pk=group_id)

    if request.user not in group.members.all() and not request.user.is_staff:
        return HttpResponseForbidden("No perteneces a este grupo.")

    group.carts.filter(active=True).update(active=False)

    cart = Cart.objects.create(group=group, active=True)
    return redirect('cart_detail', pk=cart.pk)

def cart_detail_view(request, pk):
    cart = get_object_or_404(Cart, pk=pk)
    if request.user not in cart.group.members.all() and not request.user.is_staff:
        return HttpResponseForbidden("No puedes ver este carrito.")

    cart_items = cart.cartproduct_set.select_related("product")
    products = [item.product for item in cart_items]
    total_price = sum(item.quantity * item.product.price for item in cart_items)

    return render(request, "core/cart_detail.html", {
        "cart": cart,
        "group": cart.group,
        "cart_items": cart_items,
        "products": products,
        "total_price": total_price,
        "explanation": None
    })


@require_POST
def add_product_to_cart_view(request, cart_id, product_id):
    cart = get_object_or_404(Cart, pk=cart_id)
    if request.user not in cart.group.members.all() and not request.user.is_staff:
        return HttpResponseForbidden()

    product = get_object_or_404(Product, pk=product_id)
    cp, created = CartProduct.objects.get_or_create(cart=cart, product=product)
    cp.quantity = 1 if created else cp.quantity + 1
    cp.save()

    query = request.POST.get("q", "")
    category_id = request.POST.get("category", "")
    scroll_top = request.POST.get("scrollTop", 0)

    products = Product.objects.all()
    if query:
        products = products.filter(name__icontains=query)
    if category_id:
        products = products.filter(categories__name=category_id)

    cart_items = {cp.product.id: cp.quantity for cp in CartProduct.objects.filter(cart=cart)}
    total_price = sum(cp.product.price * cp.quantity for cp in CartProduct.objects.filter(cart=cart))
    categories = Category.objects.all()

    return render(request, "core/fragments/product_search_list.html", {
        "products": products,
        "cart": cart,
        "cart_items": cart_items,
        "categories": categories,
        "total_price": total_price,
        "scroll_top": scroll_top,
    })



@require_POST
def remove_product_from_cart_view(request, cart_id, product_id):
    cart = get_object_or_404(Cart, pk=cart_id)
    if request.user not in cart.group.members.all() and not request.user.is_staff:
        return HttpResponseForbidden()

    cp = CartProduct.objects.filter(cart=cart, product_id=product_id).first()
    if cp:
        cp.quantity -= 1
        cp.save() if cp.quantity > 0 else cp.delete()

    query = request.POST.get("q", "")
    category_id = request.POST.get("category", "")
    scroll_top = request.POST.get("scrollTop", 0)

    products = Product.objects.all()
    if query:
        products = products.filter(name__icontains=query)
    if category_id:
        products = products.filter(categories__name=category_id)

    cart_items = {cp.product.id: cp.quantity for cp in CartProduct.objects.filter(cart=cart)}
    total_price = sum(cp.product.price * cp.quantity for cp in CartProduct.objects.filter(cart=cart))
    categories = Category.objects.all()

    return render(request, "core/fragments/product_search_list.html", {
        "products": products,
        "cart": cart,
        "cart_items": cart_items,
        "categories": categories,
        "total_price": total_price,
        "scroll_top": scroll_top,
    })


def cart_edit_view(request, pk):
    cart = get_object_or_404(Cart, pk=pk)
    if request.user not in cart.group.members.all() and not request.user.is_staff:
        return HttpResponseForbidden("No perteneces a este grupo")

    if not cart.active:
        return HttpResponseForbidden("Este carrito ya ha sido completado.")

    query = request.GET.get("q", "")
    category_id = request.GET.get("category", "")

    products = Product.objects.all()
    if query:
        products = products.filter(name__icontains=query)
    if category_id:
        products = products.filter(categories__name=category_id)

    cart_items = {cp.product.id: cp.quantity for cp in CartProduct.objects.filter(cart=cart)}
    total_price = sum(cp.product.price * cp.quantity for cp in CartProduct.objects.filter(cart=cart))
    categories = Category.objects.all()

    context = {
        "cart": cart,
        "group": cart.group,
        "products": products,
        "categories": categories,
        "cart_items": cart_items,
        "total_price": total_price
    }

    if request.headers.get("Hx-Request"):
        return render(request, "core/fragments/product_search_list.html", context)

    return render(request, "core/cart_edit.html", context)

@csrf_protect
def cart_clear(request, pk):
    cart = get_object_or_404(Cart, pk=pk)
    if request.method == 'POST':
        CartProduct.objects.filter(cart=cart).delete()
        return redirect('cart_edit', pk=pk)
    
@require_POST
@csrf_protect
def generate_invite_code_view(request, pk):
    group = get_object_or_404(Group, pk=pk)

    if request.user != group.creator:
        return HttpResponseForbidden("No tienes permiso para generar el código.")

    if not group.invite_code:
        group.save()

    return redirect('group_detail', pk=group.pk)


@require_POST
@csrf_protect
def order_create_view(request, cart_id):
    cart = get_object_or_404(Cart, pk=cart_id)

    if request.user != cart.group.creator and not request.user.is_staff:
        return HttpResponseForbidden("No tienes permiso para realizar esta acción.")

    if request.user not in cart.group.members.all():
        return HttpResponseForbidden()

    direccion = request.POST.get("direccion", "").strip()
    if not direccion:
        return HttpResponse("Debes especificar una dirección de envío.", status=400)

    order = Order.objects.create(
        group=cart.group,
        created_by=request.user,
        total_price=sum(cp.product.price * cp.quantity for cp in CartProduct.objects.filter(cart=cart)),
        direccion=direccion,
    )

    for cp in cart.cartproduct_set.all():
        OrderItem.objects.create(
            order=order,
            product=cp.product,
            quantity=cp.quantity,
            price=cp.product.price,
        )

    cart.active = False
    cart.save()

    return redirect('order_detail', order.pk)

def order_detail_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.user not in order.group.members.all() and request.user != order.group.creator:
        return HttpResponseForbidden("No tienes permiso para ver este pedido.")

    return render(request, "core/order_detail.html", {"order": order})

def order_list_view(request):
    orders = Order.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, "core/order_list.html", {"orders": orders})

@require_POST
@csrf_protect
def generate_cart_view(request, pk):
    group = get_object_or_404(Cart, pk=pk).group

    if request.user != group.creator and not request.user.is_staff:
        return HttpResponseForbidden("No tienes permiso para realizar esta acción.")

    if request.user not in group.members.all():
        return JsonResponse({"detail": "No tienes permiso"}, status=403)

    group_data = {
        "people_count": group.people_count,
        "duration_days": group.duration_days,
        "preferences": group.preferences,
        "restrictions": group.restrictions,
        "high_consume": group.high_consume,
        "description": group.description
    }

    products = Product.objects.all()
    product_list = "\n".join([
        f"- {p.name}: precio={p.price}€, stock={p.stock}, peso_total={p.weight_kg or 'N/A'}kg, unidades={p.units or 'N/A'}, peso/unidad={p.estimated_weight_per_unit or 'N/A'}kg. Descripción: {p.description or 'Sin descripción'}"
        for p in products
    ])

    try:
        cart_items, explanation = generate_cart_with_gpt(group_data, product_list)

        cart = Cart.objects.get(pk=pk)

        CartProduct.objects.filter(cart=cart).delete()

        for item in cart_items:
            product = Product.objects.filter(name=item["name"]).first()
            if product:
                CartProduct.objects.create(cart=cart, product=product, quantity=item["quantity"])

        cart_items = cart.cartproduct_set.select_related("product")
        products = [item.product for item in cart_items]
        total_price = sum(item.quantity * item.product.price for item in cart_items)

        context = {
            "group": group,
            "cart": cart,
            "cart_items": cart_items,
            "products": products,
            "total_price": total_price,
            "explanation": explanation
        }
        html = render_to_string("core/cart_detail.html", context, request=request)
        return HttpResponse(html)

    except Exception as e:
        return JsonResponse({"detail": f"Error al generar con IA: {str(e)}"}, status=500)