# -*- coding: utf-8 -*-
import traceback
from JobBrowserBFF.TestBase import TestBase

class JobBrowserBFFTest(TestBase):
    def test_get_job_log_happy(self):
        # TODO: get job from mock...
        job_id = '5d769018aa5a4d298c5dc97a'
        try:
            ret = self.getImpl().get_job_log(self.getContext(), {'job_id': job_id})
        except Exception as ex:
            traceback.print_tb(ex)
            self.assertTrue(False, 'Did not expect an exception: ' + str(ex.message))
            return

        self.assertIsInstance(ret, list)

        # extract first return element
        result = ret[0]
        self.assertIsInstance(result, dict)
        self.assertIn('log', result)
        job_log = result.get('log')
        self.assertIsInstance(job_log, list)
        total_count = result.get('total_count')
        self.assertIsInstance(total_count, int)

    def test_get_job_log_with_search_happy(self):
        # TODO: get job from mock...
        job_id = '5d769018aa5a4d298c5dc97a'
        try:
            ret = self.getImpl().get_job_log(self.getContext(), {
                'job_id': job_id,
                'search': ['some', 'thing'],
                'level': ['standard'],
                'offset': 0,
                'limit': 10
            })
        except Exception as ex:
            traceback.print_tb(ex)
            self.assertTrue(False, 'Did not expect an exception: ' + str(ex.message))
            return

        self.assertIsInstance(ret, list)
        result = ret[0]
        self.assertIsInstance(result, dict)
        self.assertIn('log', result)
        job = result.get('log')
        self.assertIsInstance(job, list)
        self.assertTrue(len(job) >= 1)
        total_count = result.get('total_count')
        self.assertIsInstance(total_count, int)
