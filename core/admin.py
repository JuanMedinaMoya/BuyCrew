from django.contrib import admin
from .models.product import Product
from .models.cart import Cart
from .models.cart_product import CartProduct
from .models.user import UserAccount
from .models.group import Group
from .models.category import Category
from .models.event_type import EventType

# Register your models here.
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(UserAccount)
admin.site.register(Group)
admin.site.register(Category)
admin.site.register(EventType)