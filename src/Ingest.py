import json
import datetime

from .utils import create_pg_client, create_minio_client

def ingest_data(ti):
    cnxn = create_pg_client()
    values = ti.xcom_pull(task_ids=['parse_data'])[0]
    _, prcsd_data = values

    # Type cast prior to ingestion
    for data in prcsd_data:
        data['latitude'] = round(float(data['latitude']), 4)
        data['longitude'] = round(float(data['longitude']), 4)
        data['dob'] = datetime.datetime.strptime(data['dob'].split('T')[0], '%Y-%m-%d')
        data['num_child'] = int(data['num_child'])

    input_data = [list(d.values()) for d in prcsd_data]

    with cnxn.cursor() as cursor:
        cursor.execute('BEGIN;')
        try:
            args = ','.join(cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", i).decode('utf-8') for i in input_data)
            cursor.execute(
                "INSERT INTO main.person (fname, lname, gender, nationality, address, city, state, country, latitude, longitude, email, dob, married, num_child) VALUES " + (args) + ";"
            )
            cursor.execute('COMMIT;') # Commit the changes
            print('     > Ingestion success!')
        
        except Exception as e:
            cursor.execute('ROLLBACK;') # Rollback the changes
            print('     > Ingestion failed')
            print(f'     > Error msg: {str(e)}')


def get_prcsd_data(prcsd_filename: str):
    minio = create_minio_client()
    item = minio.get_object(
            Bucket='prcsd', 
            Key=prcsd_filename
        )
    return json.loads(item['Body'].read().decode('utf-8'))