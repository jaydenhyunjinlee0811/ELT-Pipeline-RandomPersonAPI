import requests 
import queue 
import threading
import datetime
import os
import time
import json
from io import BytesIO

from .utils import create_minio_client

NUM_THREADS = 4
API_SOURCE_LINK = 'https://randomuser.me/api/'

def async_generate_data(
    num_data: int,
    run_dt: datetime.datetime
):
    output_q = queue.Queue()
    threads = list()
    output_lst = list()
        
    for _ in range(NUM_THREADS):
        thread = threading.Thread(target=single_thread_generate_data, args=(output_q, num_data))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    while not output_q.empty():
        output_lst.append(output_q.get())

    run_dt_str = datetime.datetime.strftime(run_dt, '%Y%m%dT%I%M%p')
    bucket_folder_name = run_dt_str.split('T')[0]
    output_fp = os.path.join(bucket_folder_name, f'generated_output_{run_dt_str}.json')
    return output_fp, output_lst

def single_thread_generate_data(
        q: queue.Queue,
        n: int
    ):
    for _ in range(n):
        req = requests.get(API_SOURCE_LINK)
        result = req.json()['results'][0]
        q.put(result)
        time.sleep(0.5)

# Xcom `data` from `generate_data()` to this
# Will want to write this into MiniO bucket in the future
def cache_generated_data(
    ti
):
    values = ti.xcom_pull(task_ids=['generate_data'])[0]
    stg_fn, data = values
    minio = create_minio_client()
    buckets = set(minio.list_buckets())
    data_stream = json.dumps(data).encode('utf-8')

    if 'stg' not in buckets:
        _ = minio.make_bucket('src')

    _ = minio.put_object(
        bucket_name='stg', 
        object_name=stg_fn, 
        data=BytesIO(data_stream),
        length=len(data_stream)
    )