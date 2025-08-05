# utils/gpt_cart_generator.py

from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()  # Carga variables del archivo .env

# Ahora ya tienes la API Key disponible:
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI()

def generate_cart_with_gpt(group_data, product_list):
    prompt = f"""
    Eres un asistente experto en la planificación de compras para grupos. 

    Tienes que crear un carrito de la compra para productos en función del siguiente grupo:
    - Número de personas: {group_data['people_count']}
    - Número de días: {group_data['duration_days']}
    - Preferencias del grupo: {group_data['preferences']}
    - Restricciones alimentarias o de consumo: {group_data['restrictions']}
    - El grupo consume mucha cantidad: {group_data['high_consume']}
    - Descripcion detallada del plan: {group_data['description']}

    Aquí tienes la lista de productos disponibles. Cada línea contiene:
    - Nombre del producto
    - Precio por unidad (€)
    - Stock disponible
    - Peso total del paquete (kg)
    - Número de unidades por paquete
    - Peso estimado por unidad (kg)
    - Descripción del producto

    {product_list}

    Tu tarea es seleccionar los productos y cantidades adecuadas para satisfacer al grupo durante los días indicados, considerando variedad, raciones razonables, stock disponible, y las preferencias y restricciones indicadas.
    Calcula teniendo en cuenta que si el grupo dura varios dias es para desayuno, comida y cena, las restricciones alimentarias cumplelas por persona, por ejemplo si una persona tiene una restriccion no añadas todos los productos con esa restriccion, solo para esa persona.
    Lo es importante hacer un buen calculo de las cantidades teninedo en cuenta lo que consume una persona promedio.
    La descripcion detallada es lo mas importante ahi el usuario introduce el plan que van a hacer. Ten en cuenta si proporcionan el lugar si tienen horno para hacer pizzas, barbacoa para hacer carne, etc...
    Devuelve exclusivamente un JSON con el siguiente formato exacto (sin ningún texto adicional fuera del JSON):

    {{
    "items": [
        {{ "name": "Nombre del producto", "quantity": Número de paquetes a comprar }}
    ],
    "explanation": "Breve explicación (en lenguaje natural) de por qué se han elegido esos productos y estas cantidades para cada producto, teniendo en cuenta el tipo de plan, consumo, restricciones, etc."
    }}

    No añadas ningún texto fuera de ese JSON.

    Si no hay datos calcular, estima de forma razonable basándote en el resto de información (peso, unidades o descripción). No repitas productos.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Eres un planificador de compras para grupos."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    raw = response.choices[0].message.content
    cleaned = re.sub(r"```json|```", "", raw).strip()

    try:
        print(cleaned)
        parsed = json.loads(cleaned)
        return parsed["items"], parsed.get("explanation", "")
    except json.JSONDecodeError as e:
        print("JSON malformado:", cleaned)
        raise e

