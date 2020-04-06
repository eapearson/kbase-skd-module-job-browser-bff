# -*- coding: utf-8 -*-
from JobBrowserBFF.TestBase import TestBase
from biokbase.Errors import ServiceError
import unittest

UPSTREAM_SERVICE = 'metrics'
ENV = 'ci'
USER_CLASS = 'user'
JOB_ID_HAPPY = '5b7b8287e4b0d417818a2f97'
JOB_ID_NOT_CANCELABLE = '5b7b8287e4b0d417818a2f97'
JOB_ID_NOT_FOUND = '5b7b8287e4b0d417818a2f96'
TIMEOUT_MS = 10000


class JobBrowserBFFTest(TestBase):
    # This test is tricky at present, because one has to have an active job to cancel!
    # That is, until we get some sort of mocking here.
    # Uncomment to skip this test
    @unittest.skip("skipped test_cancel_job_happy")
    def test_cancel_job_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.cancel_job(context, {
                'job_id': JOB_ID_HAPPY,
                'timeout': TIMEOUT_MS
            })
            result = ret[0]
            self.assertIsInstance(result, dict)
            # ensure it is empty (a form of void)
            self.assertFalse(result)
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_cancel_job_not_found_sad")
    def test_cancel_job_not_cancelable_sad(self):
        # I know, it is supposed to work to use assertRaises with a context object,
        # but it isn't working. Maybe the unittest version is too old, or we need to
        # use unittest2? In any case, the workaround is fine.
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.cancel_job(context, {
                'job_id': JOB_ID_NOT_CANCELABLE,
                'timeout': TIMEOUT_MS
            })
            result = ret[0]
            self.assertIsInstance(result, dict)
            # ensure it is empty (a form of void)
            self.assertFalse(result)
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_cancel_job_not_found_sad")
    def test_cancel_job_not_found_sad(self):
        # I know, it is supposed to work to use assertRaises with a context object,
        # but it isn't working. Maybe the unittest version is too old, or we need to
        # use unittest2? In any case, the workaround is fine.
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            impl.cancel_job(context, {
                'job_id': JOB_ID_NOT_FOUND,
                'timeout': TIMEOUT_MS
            })
        except ServiceError as se:
            # This is "job not found", the error which should be returned
            # in this case.
            self.assertEqual(
                se.code, 10, 'Service Error should return code "10" - for Job not found')
        except Exception as ex:
            self.assert_no_exception(ex)
