import os
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuyCrew.settings')
django.setup()

from core.models import Product, Category

productos = [
    {
        "name": "Hamburguesas de ternera 4 ud",
        "price": 4.50,
        "stock": 30,
        "weight_kg": 0.4,
        "units": 4,
        "weight_per_unit_kg": 0.1,
        "description": "Carne de ternera ideal para barbacoa.",
        "categories": ["Carnicería", "Barbacoa", "Comida"]
    },
    {
        "name": "Pizza 4 quesos",
        "price": 3.80,
        "stock": 50,
        "weight_kg": 0.45,
        "units": 1,
        "weight_per_unit_kg": 0.45,
        "description": "Pizza congelada con mezcla de quesos.",
        "categories": ["Preparados", "Comida"]
    },
    {
        "name": "Croissants 6 ud",
        "price": 2.20,
        "stock": 40,
        "weight_kg": 0.3,
        "units": 6,
        "weight_per_unit_kg": 0.05,
        "description": "Croissants dulces ideales para desayunos.",
        "categories": ["Panadería", "Desayuno", "Dulce"]
    },
    {
        "name": "Leche entera 1L",
        "price": 0.95,
        "stock": 100,
        "weight_kg": 1.0,
        "units": 1,
        "weight_per_unit_kg": 1.0,
        "description": "Leche entera UHT, básica para desayuno.",
        "categories": ["Lácteos", "Desayuno", "Bebidas"]
    },
    {
        "name": "Cerveza lata 6x33cl",
        "price": 3.60,
        "stock": 60,
        "weight_kg": 2.0,
        "units": 6,
        "weight_per_unit_kg": 0.33,
        "description": "Pack de cervezas para compartir.",
        "categories": ["Bebidas alcohólicas", "Barbacoa"]
    },
    {
        "name": "Patatas fritas 150g",
        "price": 1.30,
        "stock": 80,
        "weight_kg": 0.15,
        "units": 1,
        "weight_per_unit_kg": 0.15,
        "description": "Bolsa grande de patatas fritas para picoteo.",
        "categories": ["Snacks", "Salado"]
    },
    {
        "name": "Tortilla de patatas 600g",
        "price": 3.00,
        "stock": 25,
        "weight_kg": 0.6,
        "units": 1,
        "weight_per_unit_kg": 0.6,
        "description": "Tortilla de patatas precocinada para 3-4 personas.",
        "categories": ["Preparados", "Comida"]
    },
    {
        "name": "Pan de molde 500g",
        "price": 1.25,
        "stock": 70,
        "weight_kg": 0.5,
        "units": 20,
        "weight_per_unit_kg": 0.025,
        "description": "Ideal para desayunos y bocadillos.",
        "categories": ["Panadería", "Desayuno"]
    },
    {
        "name": "Refresco cola 2L",
        "price": 1.60,
        "stock": 90,
        "weight_kg": 2.0,
        "units": 1,
        "weight_per_unit_kg": 2.0,
        "description": "Refresco con gas sabor cola.",
        "categories": ["Bebidas"]
    },
    {
        "name": "Vasos de plástico 50 ud",
        "price": 1.90,
        "stock": 100,
        "weight_kg": 0.3,
        "units": 50,
        "weight_per_unit_kg": 0.006,
        "description": "Pack de vasos desechables para eventos.",
        "categories": ["Misceláneo"]
    },
]

def insertar_datos():
    for prod in productos:
        product, _ = Product.objects.get_or_create(
            name=prod["name"],
            defaults={
                "price": prod["price"],
                "stock": prod["stock"],
                "weight_kg": prod["weight_kg"],
                "units": prod["units"],
                "weight_per_unit_kg": prod["weight_per_unit_kg"],
                "description": prod["description"],
            }
        )

        # Asociar categorías
        category_objs = []
        for cat_name in prod["categories"]:
            category, _ = Category.objects.get_or_create(name=cat_name)
            category_objs.append(category)
        product.categories.set(category_objs)

        print(f"✅ Producto insertado o actualizado: {product.name}")

if __name__ == "__main__":
    insertar_datos()
