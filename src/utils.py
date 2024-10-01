import os
import psycopg2
from minio import Minio

def create_minio_client():
    client = Minio(
        endpoint='minio:9010',
        access_key=os.environ.get('MINIO_KEY_ID', ''),
        secret_key=os.environ.get('MINIO_ACCESS_KEY', ''),
        secure=False # For inter-container communication
    )

    return client

def create_pg_client(
    DB_NAME=os.environ.get('DB_NAME', ''),
    DB_USER=os.environ.get('DB_USER', ''),
    DB_PASS=os.environ.get('DB_PASS', ''),
    DB_HOST=os.environ.get('DB_HOST', ''),
    DB_PORT=os.environ.get('DB_PORT', ''),
):
    return psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )