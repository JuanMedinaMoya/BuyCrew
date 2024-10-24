from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, ProductView, UserView, UserRegister, UserLogin, UserLogout


router = DefaultRouter()
router.register(r'cart', CartViewSet)
router.register(r'product', ProductView)
# router.register(r'login', UserLogin)
# router.register(r'register', UserRegister)
# router.register(r'user', UserView)
# router.register(r'logout', UserLogout)

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/register/', UserRegister.as_view(), name='register'),
    path('api/v1/login/', UserLogin.as_view(), name='login'),
    path('api/v1/user/', UserView.as_view(), name='user'),
    path('api/v1/logout/', UserLogout.as_view(), name='logout'),
]
