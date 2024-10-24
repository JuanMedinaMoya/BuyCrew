from django.db import models
from .user import UserAccount
from .product import Product  # Esto no genera un problema circular.

class Cart(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, default=1)
    cart_items = models.ManyToManyField(Product, through='CartProduct')

    def __str__(self):
        return f"{self.user.username}'s cart"

    def total_price(self):
        total = sum(item.total_price() for item in self.cartproduct_set.all())
        return total

    def add_product(self, product, quantity=1):
        cart_product, created = CartProduct.objects.get_or_create(cart=self, product=product)
        if not created:
            cart_product.quantity += quantity
            cart_product.save()

    def remove_product(self, product):
        CartProduct.objects.filter(cart=self, product=product).delete()
