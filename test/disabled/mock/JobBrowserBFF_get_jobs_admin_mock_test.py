# -*- coding: utf-8 -*-
from JobBrowserBFF.TestBase import TestBase
from JobBrowserBFF.schemas.Schema import Schema
from JobBrowserBFF.Validation import Validation
import unittest

UPSTREAM_SERVICE = 'mock'
ENV='mock'
USER_CLASS = 'admin'
TIMEOUT = 10000

class JobBrowserBFFTest(TestBase):
    # Uncomment to skip this test
    # @unittest.skip("skipped test_query_jobs_filters_happy")
    def test_get_jobs_user_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        cases = [{
            'params': {
                'job_ids': [],
                'admin': 1
            },
            'expected': {
                'count': 0
            }
        },
        {
            'params': {
                'job_ids': ['5d94b6f8aa5a4d298c5dc9d7', '5d93ca04aa5a4d298c5dc9d6', '5d93b406aa5a4d298c5dc9d5'],
                'admin': 1
            },
            'expected': {
                'count': 3
            }
        }
        ]
        base_params = {
            'timeout': TIMEOUT
        }
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            for case in cases:
                params = base_params.copy()
                params.update(case['params'])
                ret = impl.get_jobs(context, params)
                jobs = self.assert_job_result(ret)
                self.assertEqual(len(jobs), case['expected']['count'])
        except Exception as ex:
            self.assert_no_exception(ex)

    # TODO: get jobs when one is not found
    # TODO: get jobs when one is not accessible
    # TODO: get jobs when all are not found
    # TODO: get jobs when all are not accessible
    # TODO: get jobs when no job ids sent