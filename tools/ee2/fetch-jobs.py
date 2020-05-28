from JobBrowserBFF.model.EE2Api import EE2Api
import os
from math import ceil
import json

url = 'https://kbase.us/services/ee2'
token = os.environ['KBASE_TOKEN']
client = EE2Api(url=url, token=token, timeout=60)
version = client.ver()
print('VERSION')
print(version)

START_TIME = 0  # 1970/1/1
END_TIME = 1609459200000  # 2021/1/1
BATCH_SIZE = 1000


def save_job(job):
    job_id = job['job_id']
    with open(f'temp/jobs/prod/{job_id}.json', 'w') as f:
        f.write(json.dumps(job, indent=4))


def save_jobs(jobs):
    for job in jobs:
        save_job(job)


def get_all_jobs():

    # get first batch
    params = {
        'start_time': START_TIME,
        'end_time': END_TIME,
        'offset': 0,
        'limit': BATCH_SIZE
    }
    result = client.check_jobs_date_range_for_all(params)
    count = result['query_count']
    print(f'count: {count}')
    batches = ceil(count / BATCH_SIZE)
    print(f'batches: {batches}')

    # save it
    save_jobs(result['jobs'])

    # now that we have the total count

    # we can loop to get all.
    for batch_number in range(1, batches):
        print(f'Batch: {batch_number}')
        params = {
            'start_time': START_TIME,
            'end_time': END_TIME,
            'offset': batch_number * BATCH_SIZE,
            'limit': BATCH_SIZE
        }
        result = client.check_jobs_date_range_for_all(params)
        save_jobs(result['jobs'])
    # save each


get_all_jobs()
