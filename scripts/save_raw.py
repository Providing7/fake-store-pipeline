import os
from pathlib import Path

import boto3
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

def find_latest_file() -> Path:
    files = sorted(DATA_DIR.glob("products_*.json"))
    if not files:
        raise FileNotFoundError(
            "Nenhum arquivo products_*.json encontrado em data/. Rode o extract.py primeiro."
        )
    return files[-1]

def upload_to_minio(client, file_path) -> None:
    client.upload_file(
        Filename=str(file_path),
        Bucket=MINIO_BUCKET,
        Key=file_path.name,
    )

def main() -> None:
    client = get_minio_client()
    file_path = find_latest_file()

    print(f"Enviando {file_path.name} para o bucket '{MINIO_BUCKET}'...")
    upload_to_minio(client, file_path)
    print("Upload concluído.")

if __name__ == "__main__":
    main()