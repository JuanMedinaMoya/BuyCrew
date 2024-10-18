from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, ProductView


router = DefaultRouter()
router.register(r'cart', CartViewSet)
router.register(r'product', ProductView)

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
