# -*- coding: utf-8 -*-
from JobBrowserBFF.TestBase import TestBase
from JobBrowserBFF.schemas.Schema import Schema
from JobBrowserBFF.Validation import Validation
import unittest

UPSTREAM_SERVICE = 'metrics'
ENV = 'ci'
USER_CLASS = 'admin'
TIMEOUT_MS = 10000
TOTAL_COUNT = 55137
FOUND_COUNT = 6465
TIMESTAMP_FROM = 1496275200000  # 6/1/17
TIMESTAMP_TO = 1527811200000  # 6/1/18


class JobBrowserBFFTest(TestBase):
    # Uncomment to skip this test
    # @unittest.skip("skipped test_query_jobs_happy")
    def test_query_jobs_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        impl, context = self.impl_for(ENV, USER_CLASS)
        try:
            ret = impl.query_jobs(context, {
                'time_span': {
                    'from': TIMESTAMP_FROM,
                    'to': TIMESTAMP_TO
                },
                'offset': 0,
                'limit': 10,
                'timeout': TIMEOUT_MS,
                'admin': 1
            })
            jobs, found_count, total_count = self.assert_job_query_result_with_count(ret)
            self.assertEqual(found_count, FOUND_COUNT)
            self.assertEqual(total_count, TOTAL_COUNT)
            self.assertEqual(len(jobs), 10)
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_query_jobs_with_time_span_happy")
    def test_query_jobs_with_sort_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        impl, context = self.impl_for(ENV, USER_CLASS)
        try:
            ret = impl.query_jobs(context, {
                'sort': [
                    {
                        'key': 'created',
                        'direction': 'ascending'
                    }
                ],
                'time_span': {
                    'from': TIMESTAMP_FROM,
                    'to': TIMESTAMP_TO
                },
                'offset': 0,
                'limit': 10,
                'timeout': TIMEOUT_MS,
                'admin': 1
            })
            jobs, found_count, total_count = self.assert_job_query_result_with_count(ret)
            self.assertEqual(found_count, FOUND_COUNT)
            self.assertEqual(total_count, TOTAL_COUNT)
            self.assertEqual(len(jobs), 10)
            self.is_in_ascending_order(jobs, ['state', 'create_at'])
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_query_jobs_with_sort_descending_happy")
    def test_query_jobs_with_sort_descending_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        impl, context = self.impl_for(ENV, USER_CLASS)
        try:
            ret = impl.query_jobs(context, {
                'sort': [
                    {
                        'key': 'created',
                        'direction': 'descending'
                    }
                ],
                'time_span': {
                    'from': TIMESTAMP_FROM,
                    'to': TIMESTAMP_TO
                },
                'offset': 0,
                'limit': 10,
                'timeout': TIMEOUT_MS,
                'admin': 1
            })
            jobs, found_count, total_count = self.assert_job_query_result_with_count(ret)
            self.assertEqual(found_count, FOUND_COUNT)
            self.assertEqual(total_count, TOTAL_COUNT)
            self.assertEqual(len(jobs), 10)
            self.is_in_descending_order(jobs, ['state', 'create_at'])
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_query_jobs_happy")
    def test_query_jobs_context_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.query_jobs(context, {
                'time_span': {
                    'from': TIMESTAMP_FROM,
                    'to': TIMESTAMP_TO
                },
                'sort': [
                    {
                        'key': 'created',
                        'direction': 'descending'
                    }
                ],
                'offset': 0,
                'limit': 20,
                'admin': 1
            })
            jobs, found_count, total_count = self.assert_job_query_result_with_count(ret)
            self.assertEqual(found_count, FOUND_COUNT)
            self.assertEqual(total_count, TOTAL_COUNT)
            self.assertEqual(len(jobs), 20)

            # for index, jobs in enumerate(jobs):
            #     print('JOB {}'.format(index), jobs)

            job1 = jobs[0]
            self.assertEqual(job1['job_id'], '5b108729e4b0d417818a2b0f')
            self.assertEqual(job1['context']['type'], 'workspace')
            self.assertEqual(job1['context']['workspace']['id'], 33074)

            job2 = jobs[9]
            self.assertEqual(job2['job_id'], '5b107c95e4b0d417818a2b06')
            self.assertEqual(job2['context']['type'], 'narrative')
            self.assertEqual(job2['context']['narrative']['title'], 'quast')

            job4 = jobs[19]
            self.assertEqual(job4['job_id'], '5b1057dee4b0d417818a2afc')
            self.assertEqual(job4['context']['type'], 'export')

        except Exception as ex:
            self.assert_no_exception(ex)
