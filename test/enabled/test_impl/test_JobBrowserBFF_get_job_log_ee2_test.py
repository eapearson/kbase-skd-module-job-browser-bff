# -*- coding: utf-8 -*-
from JobBrowserBFF.TestBase import TestBase
from biokbase.Errors import ServiceError
import unittest

UPSTREAM_SERVICE = 'ee2'
ENV = 'ci'
USER_CLASS = 'user'
JOB_ID_WITH_LOGS = '5e8285adefac56a4b4bc2b14'  # non-admin
JOB_ID_NO_LOGS = '5e8753a1efde47bd14c55dcf'  # non-admin
JOB_ID_NOT_FOUND = '5e8285adefac56a4b4bc2b13'  # non-admin
JOB_ID_NO_PERMISSION = '5dd4abecc149b420f9bb0f07'  # access it as non-admin user
JOB_ID_BATCH_PARENT = '5e864749e75488df48bb8ee5'
JOB_ID_BATCH_CHILD = '5e8647c576f5df12d4fa6953'
TIMEOUT = 10000
JOB_ID_WITH_LOGS = JOB_ID_BATCH_CHILD


class JobBrowserBFFTest(TestBase):

    def assert_job_log_result(self, result):
        self.assertIsInstance(result, dict)
        self.assertIn('log', result)
        job_log = result.get('log')
        self.assertIsInstance(job_log, list)
        total_count = result.get('total_count')
        return job_log, total_count

    # Uncomment to skip this test
    # @unittest.skip("skipped test_get_job_log_happy")
    def test_get_job_log_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.get_job_log(context, {
                'job_id': JOB_ID_WITH_LOGS,
                'offset': 0,
                'limit': 5,
                'timeout': TIMEOUT
            })
            job_log, total_count = self.assert_job_log_result(ret)
            self.assertEqual(len(job_log), 5)
            self.assertEqual(total_count, 12)
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_get_job_log_no_logs_happy")
    def test_get_job_log_no_logs_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.get_job_log(context, {
                'job_id': JOB_ID_NO_LOGS,
                'offset': 0,
                'limit': 10,
                'timeout': TIMEOUT
            })
            job_log, total_count = self.assert_job_log_result(ret)
            self.assertEqual(len(job_log), 0)
            self.assertEqual(total_count, 0)
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # Skip for now, CI jobs are down
    @unittest.skip("skipped test_get_job_log_no_permission_sad")
    def test_get_job_log_no_permission_sad(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.get_job_log(context, {
                'job_id': JOB_ID_NO_PERMISSION,
                'offset': 0,
                'limit': 10,
                'timeout': TIMEOUT
            })
            print('RET', ret)
            self.assertTrue(False, 'Expected an exception')
        except ServiceError as se:
            self.assertEqual(se.code, 40)
        except Exception as ex:
            self.assert_no_exception(ex)
