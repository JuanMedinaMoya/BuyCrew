from django.db import models
from .cart import Cart
from .product import Product

class CartProduct(models.Model):
    """
    Relación intermedia que representa un producto específico en un carrito con su cantidad.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, help_text="El carrito al que pertenece este producto")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text="El producto que está en el carrito")
    quantity = models.PositiveIntegerField(default=1, help_text="Cantidad de este producto en el carrito")

    # def __str__(self):
    #     return f"{self.quantity} {self.product.name} in {self.cart.user.username}'s cart"

    def total_price(self):
        """
        Calcula el precio total para esta cantidad del producto.
        """
        return self.product.price * self.quantity
