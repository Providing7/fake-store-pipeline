import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CSV_PATH = DATA_DIR / "product_clean.csv"

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

def get_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )

def load_clean_data() -> pd.DataFrame:
    return pd.read_csv(CSV_PATH)

def upsert_categories(conn, categories) -> dict:
    with conn.cursor() as cur:
        for category_name in categories:
            cur.execute(
                """
                INSERT INTO dim_category (category_name)
                VALUES (%s)
                ON CONFLICT (category_name) DO NOTHING
                """,
                (category_name,),
            )
        conn.commit()

        cur.execute("SELECT category_id, category_name FROM dim_category")
        rows = cur.fetchall()

    return {name: category_id for category_id, name in rows}

def upsert_products(conn, df: pd.DataFrame, category_map: dict) -> None:
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute(
                """
                INSERT INTO fact_product (product_id, product_name, price, category_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (product_id) DO UPDATE
                SET product_name = EXCLUDED.product_name,
                    price = EXCLUDED.price,
                    category_id = EXCLUDED.category_id
                """,
                (row["id"], row["title"], row["price"], category_map[row["category"]]),
            )
        conn.commit()

def main() -> None:
    df = load_clean_data()
    print(f"{len(df)} produtos carregados do CSV.")

    conn = get_connection()

    categories = df["category"].unique()
    category_map = upsert_categories(conn, categories)
    print(f"{len(category_map)} categorias na dimensão.")

    upsert_products(conn, df, category_map)
    print(f"{len(df)} produtos carregados na tabela fato.")

    conn.close()


if __name__ == "__main__":
    main()
