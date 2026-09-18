requests
pandas
boto3
psycopg2-binary
python-dotenv

requests → faz as chamadas HTTP pra Fake Store API (Fase 1)
boto3 → cliente S3-compatible, usamos pra falar com o MinIO (Fase 2)
pandas → limpeza e transformação dos dados (Fase 3)
psycopg2-binary → driver pra conectar no PostgreSQL (Fase 4)
python-dotenv → lê as credenciais do .env sem deixar senha hardcoded no código