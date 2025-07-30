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
Dado este grupo:
- Personas: {group_data['people_count']}
- Días: {group_data['duration_days']}
- Preferencias: {group_data['preferences']}
- Restricciones: {group_data['restrictions']}

Y esta lista de productos (nombre, ratio de consumo por persona/día):
{product_list}

Devuelve **únicamente** el carrito como una lista en formato JSON (sin explicaciones). Ejemplo:
[
  {{ "name": "Agua", "quantity": 4 }}
]
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
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("⚠️ JSON malformado:", cleaned)
        raise e