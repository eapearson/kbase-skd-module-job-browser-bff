# -*- coding: utf-8 -*-
from JobBrowserBFF.TestBase import TestBase
from JobBrowserBFF.schemas.Schema import Schema
from JobBrowserBFF.Validation import Validation
import unittest
import json

ENV='ci'
UPSTREAM_SERVICE = 'metrics'
TIMEOUT = 10000

class JobBrowserBFFTest(TestBase):
    def test_query_jobs_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, context = self.impl_for(ENV, 'admin')
            batch_size = 1000
            batch = 0
            while True:
                print('BATCH {}'.format(batch))
                ret = impl.query_jobs_admin(context, {
                    'time_span': {
                        'from': 0, # 1/1/70
                        'to': 1572566400000 # 11/1/19
                    },
                    'offset': batch * batch_size,
                    'limit': batch_size,
                    'timeout': TIMEOUT
                })
                jobs, found_count, total_count = self.assert_job_query_result_with_count(ret)
                for job in jobs:
                    id = job['job_id']
                    filename = '/kb/module/work/tmp/job_' + id + '.json'
                    with open(filename, 'w') as out:
                        out.write(json.dumps(job))
                if len(jobs) < batch_size:
                    break
                batch = batch + 1
        except Exception as ex:
            self.assert_no_exception(ex)
