import os
import json
from JobBrowserBFF.Validation import Validation

validation = Validation(schema_dir='ee2_api', load_schemas=True)


def validate_job(job):
    job_id = job['job_id']
    # print(f'validate? {job_id}')
    try:
        validation.validate({'$ref': 'base.json#definitions/job_state'}, job)
        # print(f'OK: {job_id}')
        print('.', end='', flush=True)
    except Exception as ex:
        print()
        print(f'ERROR {job_id}: {str(ex)}')
        print(type(ex))
        print(job)
        print()


def count_all_jobs(env):
    entries = os.scandir(f'temp/jobs/{env}')
    total = 0
    for entry in entries:
        total = total + 1
    return total


def validate_all_jobs(env):
    entries = os.scandir(f'temp/jobs/{env}')
    total_count = 0
    checkpoint_count = 0
    for entry in entries:
        total_count += 1
        checkpoint_count += 1
        if checkpoint_count == 1000:
            print()
            print(f'{total_count}')
            print()
            checkpoint_count = 0
        with open(entry, 'r') as f:
            job_json = f.read()
            job = json.loads(job_json)
            validate_job(job)
    print()
    print(f'{total_count}')
    print()


# print(count_all_jobs('prod'))
validate_all_jobs('prod')
