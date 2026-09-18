import json
import os
from pathlib import Path

import boto3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")

def get_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    )

def find_latest_object_key(client) -> str:
    response = client.list_objects_v2(Bucket=MINIO_BUCKET)
    objects = response.get("Contents", [])

    if not objects:
        raise FileNotFoundError(f"Nenhum objeto encontrado no bucket '{MINIO_BUCKET}'.")

    latest = max(objects, key=lambda obj: obj["LastModified"])
    return latest["Key"]

def load_raw_data(client, key: str) -> pd.DataFrame:
    obj = client.get_object(Bucket=MINIO_BUCKET, Key=key)
    raw_json = json.loads(obj["Body"].read())
    return pd.DataFrame(raw_json)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    # Padronizar nomes de colunas
    df.columns = df.columns.str.strip().str.lower()

    # Remover espaços extras
    df["title"] = df["title"].str.strip()
    df["category"] = df["category"].str.strip().str.lower()

    # Tratar valores nulos
    df = df.dropna(subset=["id", "title", "price", "category"])

    # Garantir consistência dos tipos de dados
    df["id"] = df["id"].astype(int)
    df["price"] = df["price"].astype(float)

    # Selecionar apenas colunas relevantes
    df = df[["id", "title", "price", "category"]]

    return df

def save_clean(df: pd.DataFrame) -> Path:
    DATA_DIR.mkdir(exist_ok=True)
    file_path = DATA_DIR / "product_clean.csv"
    df.to_csv(file_path, index=False)
    return file_path

def main() -> None:
    client = get_minio_client()
    key = find_latest_object_key(client)
    print(f"Lendo '{key}' do bucket '{MINIO_BUCKET}'...")

    df = load_raw_data(client, key)
    print(f"{len(df)} registros carregados.")

    df_clean = clean_data(df)
    print(f"{len(df_clean)} registros após a limpeza.")

    file_path = save_clean(df_clean)
    print(f"Dados tratados salvos em: {file_path}")


if __name__ == "__main__":
    main()
