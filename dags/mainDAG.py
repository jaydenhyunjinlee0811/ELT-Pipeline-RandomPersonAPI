from datetime import timedelta, datetime
from zoneinfo import ZoneInfo
import sys
import os
import dotenv
from airflow import DAG
from airflow.operators.python import PythonOperator

sys.path.insert(0, os.environ.get('PYTHONPATH', ''))

from src import (
    async_generate_data,
    cache_generated_data,
    parse_data,
    cache_parsed_data,
    ingest_data
)

_ = dotenv.load_dotenv()
DAG_NAME='Dev-ELT-Pipeline-20240926'
RUN_DT = datetime.today().astimezone(ZoneInfo('America/Los_Angeles'))
default_args = {
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    # 'retries': 1,
    # 'retry_delay': timedelta(minutes=1),
    'queue': 'bash_queue',
    # 'pool': 'backfill',
    'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    'wait_for_downstream': False,
    'sla': timedelta(hours=2),
    'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    'trigger_rule': 'all_success',
}

with DAG(
    DAG_NAME,
    default_args=default_args,
    description='Dev DAG',
    schedule_interval=None,
    start_date=datetime(2024, 4, 2),
    catchup=False,
    tags=['Dev'],
) as dag:
    task_generate_data = PythonOperator(
        task_id='generate_data',
        python_callable=async_generate_data,
        op_kwargs={'num_data': 10, 'run_dt':RUN_DT},
        do_xcom_push=True
    )
    
    task_cache_generated_data = PythonOperator(
        task_id='cache_generated_data',
        python_callable=cache_generated_data
    )

    task_parse_data = PythonOperator(
        task_id='parse_data',
        python_callable=parse_data,
        op_kwargs={'run_dt':RUN_DT},
        do_xcom_push=True
    )
    
    task_cache_parsed_data = PythonOperator(
        task_id='cache_parsed_data',
        python_callable=cache_parsed_data
    )

    task_ingest_data = PythonOperator(
        task_id='ingest_data',
        python_callable=ingest_data
    )

    task_generate_data.set_downstream(task_cache_generated_data)
    task_generate_data.set_downstream(task_parse_data)
    task_parse_data.set_downstream(task_cache_parsed_data)
    task_parse_data.set_downstream(task_ingest_data)