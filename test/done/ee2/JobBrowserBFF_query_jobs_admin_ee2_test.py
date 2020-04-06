# -*- coding: utf-8 -*-
from JobBrowserBFF.TestBase import TestBase

UPSTREAM_SERVICE = 'ee2'
TIMEOUT = 10000
ENV = 'ci'
USER_CLASS = 'admin'

TIME_FROM = 1585699200000  # 4/1/20
TIME_TO = 1585872000000  # 4/4/20


class JobBrowserBFFTest(TestBase):
    # Uncomment to skip this test
    # @unittest.skip("skipped test_query_jobs_happy")
    def test_query_jobs_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.query_jobs(context, {
                'time_span': {
                    'from': TIME_FROM,
                    'to': TIME_TO
                },
                'offset': 0,
                'limit': 5,
                'timeout': TIMEOUT,
                'admin': 1
            })
            jobs, found_count, total_count = self.assert_job_query_result_with_count(ret)
            self.assertEqual(found_count, 36)
            # TODO: total_count is not implemented in ee2 yet.
            # self.assertEqual(total_count, 19)
            self.assertEqual(len(jobs), 5)
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_query_jobs_with_time_span_happy")
    def test_query_jobs_with_sort_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.query_jobs(context, {
                'sort': [
                    {
                        'key': 'created',
                        'direction': 'ascending'
                    }
                ],
                'time_span': {
                    'from': TIME_FROM,
                    'to': TIME_TO
                },
                'offset': 0,
                'limit': 5,
                'timeout': TIMEOUT,
                'admin': 1
            })
            jobs, found_count, total_count = self.assert_job_query_result_with_count(ret)
            # self.assertEqual(total_count, 19)
            self.assertEqual(found_count, 36)
            self.is_in_ascending_order(jobs, ['state', 'create_at'])
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_query_jobs_with_sort_descending_happy")
    def test_query_jobs_with_sort_descending_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.query_jobs(context, {
                'sort': [
                    {
                        'key': 'created',
                        'direction': 'descending'
                    }
                ],
                'time_span': {
                    'from': TIME_FROM,
                    'to': TIME_TO
                },
                'offset': 0,
                'limit': 5,
                'timeout': TIMEOUT,
                'admin': 1
            })
            jobs, found_count, total_count = self.assert_job_query_result_with_count(ret)
            # self.assertEqual(total_count, 19)
            self.assertEqual(found_count, 36)
            self.is_in_descending_order(jobs, ['state', 'create_at'])
        except Exception as ex:
            self.assert_no_exception(ex)
