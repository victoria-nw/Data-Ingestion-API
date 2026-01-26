import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG={
        "host": os.getenv("DB_HOST", "localhost"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT", 5432),
}

def get_connection():
    if not all([DB_CONFIG["dbname"], DB_CONFIG["user"], DB_CONFIG["password"]]):
        raise RuntimeError("Database environment variables are not fully set")

    return psycopg2.connect(**DB_CONFIG)


