from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, ProductView, UserView, UserRegister, UserLogin, UserLogout, GroupViewSet, CategoryViewSet
from .views import login_view, register_view, home_view
from .views import (
    home_view, login_view, register_view,
    product_create_view, product_list_view,
    category_create_view, category_list_view,
    group_create_view, group_list_view,
    product_detail, product_edit, category_detail_view,
    category_edit_view, product_delete, category_delete_view,
    group_detail_view, group_edit_view, group_delete_view,
    group_join_view, cart_create_view, cart_detail_view,
    cart_edit_view, add_product_to_cart_view, remove_product_from_cart_view,
    generate_invite_code_view, order_create_view, order_detail_view,
    order_list_view, generate_cart_view, cart_clear, product_detail_card
)



router = DefaultRouter()
router.register(r'cart', CartViewSet)
router.register(r'product', ProductView)
router.register(r'groups', GroupViewSet)
router.register(r'category', CategoryViewSet)
# router.register(r'login', UserLogin)
# router.register(r'register', UserRegister)
# router.register(r'user', UserView)
# router.register(r'logout', UserLogout)

urlpatterns = [
    path('', home_view, name='home'),
    path('api/v1/', include(router.urls)),
    path('api/v1/register/', UserRegister.as_view(), name='register'),
    path('api/v1/login/', UserLogin.as_view(), name='login'),
    path('api/v1/user/', UserView.as_view(), name='user'),
    path('api/v1/logout/', UserLogout.as_view(), name='logout'), # no es necesario en el logout
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('product/create/', product_create_view, name='product_create'),
    path('product/list/', product_list_view, name='product_list_view'),
    path('product/<int:pk>/delete/', product_delete, name='product_delete'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('product/<int:pk>/edit/', product_edit, name='product_edit'),
    path('product/<int:pk>/card/', product_detail_card, name='product_detail_card'),
    path('category/create/', category_create_view, name='category_create'),
    path('category/list/', category_list_view, name='category_list'),
    path('group/create/', group_create_view, name='group_create'),
    path('group/list/', group_list_view, name='group_list'),
    path('group/<int:pk>/', group_detail_view, name='group_detail'),
    path('group/<int:pk>/edit/', group_edit_view, name='group_edit'),
    path('group/<int:pk>/delete/', group_delete_view, name='group_delete'),
    path('group/join/', group_join_view, name='group_join'),
    path('category/<str:name>/', category_detail_view, name='category_detail'),
    path('category/<str:name>/edit/', category_edit_view, name='category_edit'),
    path('category/<str:name>/delete/', category_delete_view, name='category_delete'),
    path('cart/create/<int:group_id>/', cart_create_view, name='cart_create'),
    path('cart/<int:pk>/', cart_detail_view, name='cart_detail'),
    path("cart/<int:pk>/edit/", cart_edit_view, name="cart_edit"),
    path("cart/<int:cart_id>/add/<int:product_id>/", add_product_to_cart_view, name="cart_add_item"),
    path('cart/<int:pk>/clear/', cart_clear, name='cart_clear'),
    path("cart/<int:cart_id>/remove/<int:product_id>/", remove_product_from_cart_view, name="cart_remove_item"),
    path('cart/<int:pk>/generate/', generate_cart_view, name='cart_generate'),
    path('group/<int:pk>/generate_invite/', generate_invite_code_view, name='generate_invite_code'),
    path('order/create/<int:cart_id>/', order_create_view, name='order_create'),
    path('order/<int:pk>/', order_detail_view, name='order_detail'),
    path('orders/', order_list_view, name='order_list'),
]



urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
