from django.db import models
from .category import Category

class Product(models.Model):
    """
    Modelo que representa un producto disponible en la tienda.
    """
    name = models.TextField(max_length=100, help_text="Nombre del producto")
    price = models.DecimalField(max_digits=6, decimal_places=2, help_text="Precio del producto")
    stock = models.PositiveIntegerField(default=0, help_text="Cantidad disponible en el inventario")
    categories = models.ManyToManyField(Category, related_name='products')

    image = models.ImageField(upload_to='product_images/', blank=True, null=True, help_text="Imagen del producto")

    weight_kg = models.FloatField(
        null=True, blank=True,
        help_text="Peso total o capacidad del paquete del producto (en kilogramos o Litros). Ej: 0.5 para 500 gramos"
    )

    units = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Cantidad de unidades individuales que contiene el paquete. Ej: 6 para un pack de 6 latas"
    )

    weight_per_unit_kg = models.FloatField(
        null=True, blank=True,
        help_text="Peso o capacidad de una unidad del producto, si aplica (en kilogramos o litros). Ej: 0.33 para una lata de 330 ml"
    )

    description = models.TextField(
        blank=True,
        help_text="Descripción del producto (ingredientes, uso, etc.) para ayudar a OpenAI a planificar mejor"
    )

    def __str__(self):
        return self.name

    @property
    def estimated_weight_per_unit(self):
        """
        Si no se ha especificado el peso por unidad, intenta calcularlo a partir del peso total y unidades.
        """
        if self.weight_per_unit_kg:
            return self.weight_per_unit_kg
        if self.weight_kg and self.units:
            return round(self.weight_kg / self.units, 3)
        return None

    @property
    def estimated_total_weight(self):
        """
        Si no se ha especificado el peso total, intenta calcularlo a partir del peso por unidad y unidades.
        """
        if self.weight_kg:
            return self.weight_kg
        if self.weight_per_unit_kg and self.units:
            return round(self.weight_per_unit_kg * self.units, 3)
        return None