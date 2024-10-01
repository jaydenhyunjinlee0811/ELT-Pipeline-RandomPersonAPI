import datetime
from zoneinfo import ZoneInfo
import os
import dotenv

from src import (
    async_generate_data, 
    cache_generated_data, 
    parse_data, 
    cache_parsed_data,
    ingest_data
)

WORKDIR = os.getcwd()
RUN_DT = datetime.datetime.today().astimezone(ZoneInfo('America/Los_Angeles'))
REPL_FACTOR=50
MARTIAL_STATUS = ['Y', 'N']

if __name__ == '__main__':
    print('Initiating pipeline'.center(REPL_FACTOR-10, '-'))
    _ = dotenv.load_dotenv()

    print(' > Requesting sample data from source..')
    stg_fn, gen_lst = async_generate_data(
        num_data=20,
        run_dt=RUN_DT
    )

    print(' > Caching collected data into staging bucket..')
    _ = cache_generated_data(
        data=gen_lst,
        filename=stg_fn
    )
    print('-'*REPL_FACTOR)
    
    print(' > Parsing through unprocessed staging data..')
    prcsd_fn, prcsd_lst = parse_data(
        stg_data=gen_lst,
        run_dt=RUN_DT
    )

    print(' > Caching processed data into processed bucket..')
    _ = cache_parsed_data(
        prcsd_lst,
        filename=prcsd_fn
    )
    print('-'*REPL_FACTOR)

    print(' > Ingesting processed data into target database..')
    _ = ingest_data(prcsd_lst)
    print('-'*REPL_FACTOR)
    
    print('End of pipeline'.center(REPL_FACTOR-10, '-'))