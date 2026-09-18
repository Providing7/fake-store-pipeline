DROP TABLE IF EXISTS fact_product;
DROP TABLE IF EXISTS dim_category;

CREATE TABLE dim_category (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE fact_product (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    category_id INTEGER NOT NULL REFERENCES dim_category(category_id)
);
