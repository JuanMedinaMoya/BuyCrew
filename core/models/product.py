from django.db import models

class Product(models.Model):
    """
    Modelo que representa un producto disponible en la tienda.
    """
    name = models.TextField(max_length=100, help_text="Nombre del producto")
    price = models.DecimalField(max_digits=6, decimal_places=2, help_text="Precio del producto")
    stock = models.PositiveIntegerField(default=0, help_text="Cantidad disponible en el inventario")

    def __str__(self):
        return self.name