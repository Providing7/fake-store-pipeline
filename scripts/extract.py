import json
from datetime import datetime, timezone
from pathlib import Path

import requests

API_URL = "https://fakestoreapi.com/products"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def fetch_products(url: str) -> list:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()

def validate_products(products: list) -> None:
    if not isinstance(products, list) or len(products) == 0:
        raise ValueError("A API não retornou uma lista de produtos válida :(")

    required_keys = {"id", "title", "price", "description", "category"} 
    for product in products: 
        missing = required_keys - product.keys()
        if missing:
            raise ValueError(f"Produto {product.get('id')} sem os campos: {missing}")

def save_temp(products: list) -> Path:
    DATA_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    file_path = DATA_DIR / f"products_{timestamp}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    return file_path

def main() -> None:
    print(f"Extraindo dados de {API_URL}...")
    products = fetch_products(API_URL)
    print(f"{len(products)} produtos recebidos.")

    validate_products(products)
    print("Validação concluída: todos os produtos têm os campos obrigatórios.")

    file_path = save_temp(products)
    print(f"Dados salvos temporariamente em: {file_path}")

if __name__ == "__main__":
    main()