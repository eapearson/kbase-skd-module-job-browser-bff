# -*- coding: utf-8 -*-
from JobBrowserBFF.TestBase import TestBase
from JobBrowserBFF.schemas.Schema import Schema
from JobBrowserBFF.Validation import Validation
import unittest

UPSTREAM_SERVICE = 'ee2'
TIMEOUT = 10000

class JobBrowserBFFTest(TestBase):
    # Uncomment to skip this test
    # @unittest.skip("skipped test_query_jobs_happy")
    def test_query_jobs_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, ctx = self.newImplCtx('test_token_admin')
            ret = impl.query_jobs_admin(ctx, {
                'time_span': {
                    'from': 1496275200000, # 6/1/17
                    'to': 1527811200000 # 6/1/18
                },
                'offset': 0,
                'limit': 10,
                'timeout': TIMEOUT
            })
            jobs, found_count, total_count = self.assert_job_query_result_with_count(ret)
            self.assertEqual(found_count, 184)
            # TODO: change to actual total count when fixed upstream
            # self.assertEqual(found_count, 2320)
            self.assertEqual(len(jobs), 10)
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_query_jobs_with_time_span_happy")
    def test_query_jobs_with_sort_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, ctx = self.newImplCtx('test_token_admin')
            ret = impl.query_jobs_admin(ctx, {
                'sort': [
                    {
                        'key': 'created',
                        'direction': 'ascending'
                    }
                ],
                'time_span': {
                    'from': 1496275200000, # 6/1/17
                    'to': 1527811200000 # 6/1/18
                },
                'offset': 0,
                'limit': 10,
                'timeout': TIMEOUT
            })
            jobs, found_count, total_count = self.assert_job_query_result_with_count(ret)
            self.assertEqual(found_count, 184)
            # TODO: change to actual total count when fixed upstream
            # self.assertEqual(total_count, 2320)
            self.assertEqual(len(jobs), 10)
            self.is_in_ascending_order(jobs, ['state', 'create_at'])
        except Exception as ex:
           self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_query_jobs_with_sort_descending_happy")
    def test_query_jobs_with_sort_descending_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, ctx = self.newImplCtx('test_token_admin')
            ret = impl.query_jobs_admin(ctx, {
                'sort': [
                    {
                        'key': 'created',
                        'direction': 'descending'
                    }
                ],
                'time_span': {
                    'from': 1496275200000, # 6/1/17
                    'to': 1527811200000 # 6/1/18
                },
                'offset': 0,
                'limit': 10,
                'timeout': TIMEOUT
            })
            jobs, found_count, total_count = self.assert_job_query_result_with_count(ret)
            self.assertEqual(found_count, 184)
            # TODO: change to actual total count when fixed upstream
            # self.assertEqual(total_count, 2320)
            self.assertEqual(len(jobs), 10)
            self.is_in_descending_order(jobs, ['state', 'create_at'])
        except Exception as ex:
            self.assert_no_exception(ex)

   