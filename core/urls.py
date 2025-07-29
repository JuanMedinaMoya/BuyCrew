from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, ProductView, UserView, UserRegister, UserLogin, UserLogout, GroupViewSet, CategoryViewSet, EventTypeViewSet
from .views import login_view, register_view, home_view
from .views import (
    home_view, login_view, register_view,
    product_create_view, product_list_view,
    category_create_view, category_list_view,
    group_create_view, group_list_view,
    event_type_create_view, event_type_list_view,
)



router = DefaultRouter()
router.register(r'cart', CartViewSet)
router.register(r'product', ProductView)
router.register(r'groups', GroupViewSet)
router.register(r'category', CategoryViewSet)
router.register(r'event-type', EventTypeViewSet)
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
    path('product/create/', product_create_view),
    path('product/list/', product_list_view),
    path('category/create/', category_create_view),
    path('category/list/', category_list_view),
    path('group/create/', group_create_view),
    path('group/list/', group_list_view),
    path('event_type/create/', event_type_create_view),
    path('event_type/list/', event_type_list_view),
]
