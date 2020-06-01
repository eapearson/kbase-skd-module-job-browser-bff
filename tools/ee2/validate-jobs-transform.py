import os
import json
from JobBrowserBFF.Validation import Validation
from JobBrowserBFF.model.EE2Model import EE2Model
from JobBrowserBFF.model.KBaseServices import KBaseServices

validation = Validation(schema_dir='impl', load_schemas=True)

schema = {
    'type': 'array',
    'items': {
        '$ref': 'base.json#definitions/job_info'
    }
}

token = os.environ['KBASE_TOKEN']

env = 'prod'

config = {
    'ee2-url': 'https://kbase.us/services/ee2',
    'workspace-url': 'https://kbase.us/services/ws',
    'auth-url': 'https://kbase.us/services/auth',
    'catalog-url': 'https://kbase.us/services/catalog',
    'nms-url': 'https://kbase.us/services/narrative_method_store/rpc'
}

model = EE2Model(
    config=config,
    token=token,
    timeout=60,
    username="eapearson"
)

services = KBaseServices(config=config, token=token)


def validate_job(job):
    job_id = job['job_id']
    jobs2 = None
    try:
        jobs2 = model.raw_jobs_to_jobs([job], services=services)
        validation.validate(schema, jobs2)
        print('.', end='', flush=True)
    except Exception as ex:
        print()
        print(f'ERROR {job_id}: {str(ex)}')
        print(type(ex))
        print(jobs2)
        print(json.dumps(job, indent=4))
        print()


def validate_all_jobs(start):
    print(f'Starting at {start}')
    entries = os.scandir('temp/jobs/prod')
    total_count = 0
    checkpoint_count = 0
    for entry in entries:
        total_count += 1
        if total_count < start:
            continue
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


validate_all_jobs(45000)
