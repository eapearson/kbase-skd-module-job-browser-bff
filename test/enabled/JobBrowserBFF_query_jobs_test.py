# -*- coding: utf-8 -*-
from JobBrowserBFF.TestBase import TestBase

class JobBrowserBFFTest(TestBase):
    def test_query_jobs_happy(self):
        try:
            ret = self.getImpl().query_jobs(self.getContext(), {
                'users': ['eapearson'],
                # 'jobs': ['5d769018aa5a4d298c5dc97a'],
                'sort': [
                    {
                        'key': 'narrative',
                        'direction': 'ascending'
                    }
                ],
                # 'search': ['my', 'search', 'string'],
                # 'date_range': {
                #     'from': 0,
                #     'to': 1
                # },
                'client_groups': ['njs'],
                'offset': 0,
                'limit': 10
            })
            result = ret[0]
            self.assertIsInstance(result, dict)
            self.assertIsInstance(result, dict)
            self.assertIn('jobs', result)
            jobs = result['jobs']
            self.assertIsInstance(jobs, list)
            self.assertIn('total_count', result)
            total_count = result['total_count']
        except Exception as ex:
            #    traceback.print_tb(ex)
           self.assertTrue(False, 'Did not expect an exception: ' + str(ex.message))
           return

    def test_query_jobs_with_date_range_happy(self):
        try:
            ret = self.getImpl().query_jobs(self.getContext(), {
                'users': ['eapearson'],
                # 'jobs': ['5d769018aa5a4d298c5dc97a'],
                'sort': [
                    {
                        'key': 'narrative',
                        'direction': 'ascending'
                    }
                ],
                # 'search': ['my', 'search', 'string'],
                'date_range': {
                    'from': 1546375830000, # 1/1/19
                    'to': 1567371030000 # 9/1/19
                },
                # 'client_groups': ['njs'],
                'offset': 0,
                'limit': 10
            })
            result = ret[0]
            self.assertIsInstance(result, dict)
            self.assertIn('jobs', result)
            jobs = result['jobs']
            self.assertIsInstance(jobs, list)
            self.assertIn('total_count', result)
            total_count = result['total_count']
            # TODO: more tests on the result.
            # TODO: practically, this requires mocking the call
            #       so we have deterministic results!
        except Exception as ex:
            #    traceback.print_tb(ex)
           self.assertTrue(False, 'Did not expect an exception: ' + str(ex.message))
           return

