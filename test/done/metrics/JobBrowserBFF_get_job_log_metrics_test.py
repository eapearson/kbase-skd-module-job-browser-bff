# -*- coding: utf-8 -*-
import traceback
from JobBrowserBFF.TestBase import TestBase
from biokbase.Errors import ServiceError
import unittest
import re

UPSTREAM_SERVICE = 'metrics'
ENV = 'ci'
USER_CLASS = 'user'
JOB_ID_WITH_LOGS = '59820c93e4b06f68bf751eeb'  # non-admin
JOB_ID_NO_LOGS = '5cf1522aaa5a4d298c5dc2ff'  # non-admin
JOB_ID_NOT_FOUND = '5cf1522aaa5a4d298c5dc2fe'  # non-admin
JOB_ID_NO_PERMISSION = '5dbb4d80062b8c2a0a69e271'  # access it as non-admin user
TIMEOUT_MS = 10000


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
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.get_job_log(context, {
                'job_id': JOB_ID_WITH_LOGS,
                'offset': 0,
                'limit': 10,
                'timeout': TIMEOUT_MS
            })
            job_log, total_count = self.assert_job_log_result(ret)
            self.assertEqual(len(job_log), 10)
            self.assertEqual(total_count, 215)
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_get_job_log_happy")
    def test_get_job_log_no_logs_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        job_id = JOB_ID_NO_LOGS
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.get_job_log(context, {
                'job_id': job_id,
                'offset': 0,
                'limit': 10,
                'timeout': TIMEOUT_MS
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
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.get_job_log(context, {
                'job_id': JOB_ID_NO_PERMISSION,
                'offset': 0,
                'limit': 10,
                'timeout': TIMEOUT_MS
            })
            print('RET', ret)
            self.assertTrue(False, 'Expected an exception')
        except ServiceError as se:
            self.assertEqual(se.code, 40)
        except Exception as ex:
            self.assert_no_exception(ex)
