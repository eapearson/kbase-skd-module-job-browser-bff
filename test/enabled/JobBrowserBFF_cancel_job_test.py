# -*- coding: utf-8 -*-
from JobBrowserBFF.TestBase import TestBase

class JobBrowserBFFTest(TestBase):
    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_cancel_job_happy(self):
        try:
            ret = self.getImpl().cancel_job(self.getContext(), {
                'job_id': '5d769018aa5a4d298c5dc97a'
            })
        except Exception as ex:
            #    traceback.print_tb(ex)
           self.assertTrue(False, 'Did not expect an exception: ' + str(ex.message))
           return

        self.assertIsInstance(ret, list)
        result = ret[0]
        self.assertIsInstance(result, dict)
        self.assertIn('canceled', result)
        is_canceled = result.get('canceled')
        self.assertIsInstance(is_canceled, bool)
        self.assertEqual(is_canceled, True)
