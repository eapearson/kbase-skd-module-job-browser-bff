from JobBrowserBFF.model.EE2Api import EE2Api
import os
import json
import datetime
import time
import math

url = 'https://ci.kbase.us/services/ee2'
token = os.environ['KBASE_TOKEN']
client = EE2Api(url=url, token=token, timeout=60)
version = client.ver()
print('VERSION')
print(version)

START_TIME = 0  # 1970/1/1
END_TIME = 1609459200000  # 2021/1/1
BATCH_SIZE = 1000


def save_job(data, iter):
    job_id = data['job']['job_id']
    with open('temp/drift/{}-{:03d}.json'.format(job_id, iter), 'w') as f:
        f.write(json.dumps(data, indent=4))


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

    analysis = dict()
    now = round(time.time() * 1000)
    created = result['created']
    analysis['created'] = {
        'diff': now - created,
        'now': now,
        'created': created
    }

    queued = result.get('queued')
    if queued is not None:
        analysis['queued'] = {
            'diff': now - queued,
            'now': now,
            'queued': queued
        }

    running = result.get('running')
    if running is not None:
        analysis['running'] = {
            'diff': now - running,
            'now': now,
            'queued': running
        }

    # count = result['query_count']
    # print('NOW?')
    # print(now)
    # print(created)
    # print(result)
    return {
        'analysis': analysis,
        'job': result
    }
    # return result


def monitor_last_job(iters):
    try:
        for iter in range(iters):
            job = get_last_job()
            save_job(job, iter)
    except Exception as ex:
        print('ERROR!')
        print(ex.message)


monitor_last_job(100)
