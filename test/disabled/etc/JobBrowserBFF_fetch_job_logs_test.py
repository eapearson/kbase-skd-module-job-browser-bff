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
            batch_size = 100
            batch = 480
            while True:
                print('BATCH {}'.format(batch))
                ret = impl.query_jobs(context, {
                    'time_span': {
                        'from': 0, # 1/1/70
                        'to': 1572566400000 # 11/1/19
                    },
                    'offset': batch * batch_size,
                    'limit': batch_size,
                    'timeout': TIMEOUT,
                    'admin': 1
                })
                jobs, found_count, total_count = self.assert_job_query_result_with_count(ret)
                for job in jobs:
                    id = job['job_id']

                    ret = impl.get_job_log(context, {
                        'job_id': id,
                        'offset': 0,
                        'limit': 100000,
                        'timeout': TIMEOUT
                    })
                    log = ret[0]['log']
                    if len(log) == 0:
                        continue
                    filename = '/kb/module/work/tmp/job_log_' + id + '.json'
                    log_doc = {
                        'job_id': id,
                        'log': log
                    }
                    with open(filename, 'w') as out:
                        out.write(json.dumps(log_doc))
                if len(jobs) < batch_size:
                    break
                batch = batch + 1
        except Exception as ex:
            self.assert_no_exception(ex)
