import datetime
import json
import os
import random 
from io import BytesIO
from typing import List

from .utils import create_minio_client

MARTIAL_STATUS = ['Y', 'N']

def parse_data(
    ti,
    run_dt: datetime.datetime
):
    '''
    Returns filename, or bucketpath, to where the processed data will get stored in
    '''
    values = ti.xcom_pull(task_ids=['generate_data'][0])
    _, stg_data = values
    output_lst = list()

    print('     > Parsing through each of the personal data..')
    for idx, item in enumerate(stg_data):
        address = ' '.join([
            str(item['location']['street']['number']),
            item['location']['street']['name']
        ])
        parsed_d = {
            'fname': item['name']['first'],
            'lname': item['name']['last'],
            'gender': item['gender'],
            'nationality': item['nat'],
            'address': address,
            'city': item['location']['city'],
            'state': item['location']['state'],
            'country': item['location']['country'],
            'latitude': float(item['location']['coordinates']['latitude']),
            'longitude': float(item['location']['coordinates']['longitude']),
            'email': item['email'],
            'dob': item['dob']['date'],
            'married': random.sample(MARTIAL_STATUS, k=1).pop(0)
        }
        if parsed_d['married'] == 'Y':
            num_child = random.sample(range(1,6), k=1).pop(0)
        else:
            num_child = 0

        parsed_d['num_child'] = num_child
        output_lst.append(parsed_d)
        print(f'     > Parsing {idx+1}th staging data complete!')

    print('     > Parsing complete!')
    run_dt_str = datetime.datetime.strftime(run_dt, '%Y%m%dT%I%M%p')
    bucket_folder_name = run_dt_str.split('T')[0]
    output_fp = os.path.join(bucket_folder_name, f'parsed_output_{run_dt_str}.json')
    return output_fp, output_lst

def get_stg_data(stg_filename: str) -> List[bytes]:
    '''
    Takes bucket path, or filename, of the newly generated dataset
    Returns list of dictionary of each personal information
    '''
    print('     > Collecting newly landed staging data from staging bucket..')
    minio = create_minio_client()
    item = minio.get_object(
            bucket_name='stg', 
            object_name=stg_filename
        )
    return json.loads(item['Body'].read().decode('utf-8'))

def cache_parsed_data(
    ti
):
    values = ti.xcom_pull(task_ids=['parse_data'])[0]
    prcsd_fn, data = values
    minio = create_minio_client()
    buckets = set(minio.list_buckets())
    data_stream = json.dumps(data).encode('utf-8')

    if 'prcsd' not in buckets:
        _ = minio.make_bucket('prcsd')

    _ = minio.put_object(
        bucket_name='prcsd', 
        object_name=prcsd_fn, 
        data=BytesIO(data_stream),
        length=len(data_stream)
    )