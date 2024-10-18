from django.contrib import admin
from .models.product import Product
from .models.cart import Cart
from .models.cart_product import CartProduct


# Register your models here.
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartProduct)