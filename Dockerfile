FROM apache/airflow

USER root 

RUN apt-get update && apt-get -y install libpq-dev gcc

USER airflow 

RUN pip install --no-cache-dir requests minio psycopg2-binary
