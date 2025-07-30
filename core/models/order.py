from django.db import models
from .group import Group
from .user import UserAccount
from .product import Product

class Order(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='orders')
    created_by = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    direccion = models.CharField(max_length=255) 
    notes = models.TextField(blank=True)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"Pedido del grupo {self.group.name} - {self.created_at.strftime('%d/%m/%Y')}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
