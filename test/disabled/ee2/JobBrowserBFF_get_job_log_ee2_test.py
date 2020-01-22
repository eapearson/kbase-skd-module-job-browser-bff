# -*- coding: utf-8 -*-
import traceback
from JobBrowserBFF.TestBase import TestBase
from biokbase.Errors import ServiceError
import unittest
import re

UPSTREAM_SERVICE = 'ee2'
JOB_ID_WITH_LOGS ='5dd4abecc149b420f9bb0f07' # non-admin
JOB_ID_NO_LOGS = '5cf1522aaa5a4d298c5dc2ff' # non-admin
JOB_ID_NOT_FOUND = '5dd4abecc149b420f9bb0f06' # non-admin
JOB_ID_NO_PERMISSION = '5dd4abecc149b420f9bb0f07' # access it as non-admin user
TIMEOUT = 10000

class JobBrowserBFFTest(TestBase):

    def assert_job_log_result(self, ret):
        self.assertIsInstance(ret, list)
        result = ret[0]
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
            impl, context = self.impl_for('user')
            ret = impl.get_job_log(context, {
                'job_id': JOB_ID_WITH_LOGS,
                'offset': 0,
                'limit': 10,
                'timeout': TIMEOUT
                })
            job_log, total_count = self.assert_job_log_result(ret)
            self.assertEqual(len(job_log), 10)
            self.assertEqual(total_count, 4375)
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_get_job_log_happy")
    def test_get_job_log_no_logs_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        job_id = JOB_ID_NO_LOGS
        try:
            impl, context = self.impl_for('user')
            ret = impl.get_job_log(context, {
                'job_id': job_id,
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
    # @unittest.skip("skipped test_get_job_log_happy")
    def test_get_job_log_no_permission_sad(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        job_id = JOB_ID_NO_LOGS
        try:
            impl, context = self.impl_for('user')
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

