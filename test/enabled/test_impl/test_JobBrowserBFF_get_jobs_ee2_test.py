# -*- coding: utf-8 -*-
from JobBrowserBFF.TestBase import TestBase
from biokbase.Errors import ServiceError
# import unittest
# import json
# import traceback

ENV = 'ci'
USER_CLASS = 'user'
UPSTREAM_SERVICE = 'ee2'
JOB_ID_HAPPY = '5e8285adefac56a4b4bc2b14'
JOB_ID_NOT_FOUND = '5dcb4324fdf6d14ac59ea916'
TIMEOUT = 10000


class JobBrowserBFFTest(TestBase):
    # Uncomment to skip this test
    # @unittest.skip("skipped test_get_jobs_happy")
    def test_get_jobs_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        impl, context = self.impl_for(ENV, USER_CLASS)
        params = {
            'job_ids': [JOB_ID_HAPPY],
            'timeout': TIMEOUT
        }
        try:
            ret = impl.get_jobs(context, params)
            jobs = self.assert_job_result(ret)
            self.assertEqual(len(jobs), 1)
            job = jobs[0]
            self.assertEqual(job['job_id'], JOB_ID_HAPPY)
            self.assertEqual(job['owner']['realname'], 'KBase UI Test User')
            self.assertEqual(job['app']['title'], 'Assemble Reads with MEGAHIT')
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_get_jobs_no_job_ids_happy")
    def test_get_jobs_no_job_ids_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        impl, context = self.impl_for(ENV, USER_CLASS)
        params = {
            'job_ids': [],
            'timeout': TIMEOUT
        }
        try:
            ret = impl.get_jobs(context, params)
            jobs = self.assert_job_result(ret)
            self.assertEqual(len(jobs), 0)
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_get_jobs_not_found_sad")
    def test_get_jobs_not_found_sad(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        impl, context = self.impl_for(ENV, USER_CLASS)
        params = {
            'job_ids': [JOB_ID_NOT_FOUND],
            'timeout': TIMEOUT
        }
        try:
            impl.get_jobs(context, params)
            self.assertFalse(True, 'Expected to raise an exception')
        except ServiceError as se:
            # This is "job not found", the error which should be returned
            # in this case.
            self.assertEqual(
                se.code, 10, 'Service Error should return code "10" - for Job not found')
        except Exception as ex:
            self.assert_no_exception(ex)
