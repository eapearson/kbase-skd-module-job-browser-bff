# -*- coding: utf-8 -*-
from JobBrowserBFF.TestBase import TestBase
from biokbase.Errors import ServiceError
import unittest

UPSTREAM_SERVICE = 'mock'
ENV = 'mock'
USER_CLASS = 'user'
JOB_ID_HAPPY = '5b7b8287e4b0d417818a2f97'
JOB_ID_NOT_CANCELABLE = '59820c93e4b06f68bf751eeb'  # complete, not cancelable
JOB_ID_NOT_FOUND = '5cf1522aaa5a4d298c5dc2fe'  # does not exist at all
# owned by eaptest34 user other than 'user' and 'admin'
JOB_ID_OTHER_USER_NOT_OWNER = '57f2dccfe4b0b05cf8996c43'
TIMEOUT = 10000


class JobBrowserBFFTest(TestBase):
    # This test is tricky at present, because one has to have an active job to cancel!
    # TODO: insert cancellable job into mongo, remove it afterwards
    # Uncomment to skip this test
    @unittest.skip("skipped test_cancel_job_happy")
    def test_cancel_job_happy(self):
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, context = self.impl_for(ENV, 'user')
            ret = impl.cancel_job(context, {
                'job_id': JOB_ID_HAPPY,
                'timeout': TIMEOUT
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
            impl, context = self.impl_for(ENV, 'user')
            ret = impl.cancel_job(context, {
                'job_id': JOB_ID_NOT_CANCELABLE,
                'timeout': TIMEOUT
            })
            result = ret[0]
            self.assertIsInstance(result, dict)
            # ensure it is empty (a form of void)
            self.assertFalse(result)
        except ServiceError as se:
            if se.code == 60:
                self.assertTrue(True)
            else:
                self.assertTrue(False, 'Unexpected service error: {}'.se.code)
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
            impl, context = self.impl_for(ENV, 'user')
            impl.cancel_job(context, {
                'job_id': JOB_ID_NOT_FOUND,
                'timeout': TIMEOUT
            })
        except ServiceError as se:
            # This is "job not found", the error which should be returned
            # in this case.
            self.assertEqual(
                se.code, 10,
                f'''Service Error should return code "10" - for Job not found; \
                got {se.code} - {se.message}\
                ''')
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_cancel_job_not_found_sad")

    def test_cancel_access_denied_sad(self):
        # I know, it is supposed to work to use assertRaises with a context object,
        # but it isn't working. Maybe the unittest version is too old, or we need to
        # use unittest2? In any case, the workaround is fine.
        self.set_config('upstream-service', UPSTREAM_SERVICE)
        try:
            impl, context = self.impl_for(ENV, 'user')
            impl.cancel_job(context, {
                'job_id': JOB_ID_OTHER_USER_NOT_OWNER,
                'timeout': TIMEOUT
            })
        except ServiceError as se:
            # This is "job not found", the error which should be returned
            # in this case.
            self.assertEqual(
                se.code, 40,
                f'''Service Error should return code "10" - for Job not found;\
                 got {se.code} - {se.message}\
                ''')
        except Exception as ex:
            self.assert_no_exception(ex)
