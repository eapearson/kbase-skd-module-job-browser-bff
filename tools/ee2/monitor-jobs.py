from JobBrowserBFF.model.EE2Api import EE2Api
import os
import json

url = 'https://ci.kbase.us/services/ee2'
token = os.environ['KBASE_TOKEN']
client = EE2Api(url=url, token=token, timeout=60)
version = client.ver()
print('VERSION')
print(version)

START_TIME = 0  # 1970/1/1
END_TIME = 1609459200000  # 2021/1/1
BATCH_SIZE = 1000


def save_job(job, iter):
    job_id = job['job_id']
    with open('temp/monitor/{}-{:03d}.json'.format(job_id, iter), 'w') as f:
        f.write(json.dumps(job, indent=4))


def get_last_job():
    # get first batch
    params = {
        'start_time': START_TIME,
        'end_time': END_TIME,
        'offset': 0,
        'limit': 1,
        'ascending': 0
    }
    result = client.check_jobs_date_range_for_all(params)['jobs'][0]
    # count = result['query_count']
    return result


def monitor_last_job(iters):
    for iter in range(iters):
        job = get_last_job()
        save_job(job, iter)


monitor_last_job(100)
