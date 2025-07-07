from django.db import models
from .group import Group
from .product import Product  # Esto no genera un problema circular.

class Cart(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="cart")
    cart_items = models.ManyToManyField(Product, through='CartProduct')

    def __str__(self):
        return f"{self.group.name}'s cart"

    def total_price(self):
        total = sum(item.total_price() for item in self.cartproduct_set.all())
        return total

    def add_product(self, product, quantity=1):
        from .cart_product import CartProduct
        cart_product, created = CartProduct.objects.get_or_create(cart=self, product=product)
        if not created:
            cart_product.quantity += quantity
        else:
            cart_product.quantity = quantity
        cart_product.save()

    def remove_product(self, product):
        from .cart_product import CartProduct
        CartProduct.objects.filter(cart=self, product=product).delete()