# -*- coding: utf-8 -*-
from JobBrowserBFF.TestBase import TestBase
import json

class JobBrowserBFFTest(TestBase):
    def test_get_jobs_happy(self):
        try:
            ret = self.getImpl().get_jobs(self.getContext(), {'job_ids': ['5d769018aa5a4d298c5dc97a']})
        except Exception as ex:
            #    traceback.print_tb(ex)
           self.assertTrue(False, 'Did not expect an exception: ' + str(ex))
           return

        self.assertIsInstance(ret, list)
        result = ret[0]
        self.assertIsInstance(result, dict)
        self.assertIn('jobs', result)
        jobs = result.get('jobs')
        self.assertIsInstance(jobs, list)
        self.assertEqual(len(jobs), 1)
        job = jobs[0]
        self.assertEqual(job['job_id'], '5d769018aa5a4d298c5dc97a')
        self.assertEqual(job['owner']['realname'], 'Erik A. Pearson')
        self.assertEqual(job['app']['title'], 'Annotate Assembly and ReAnnotate Genomes with Prokka v1.12')

    def test_get_jobs_no_job_ids_happy(self):
        try:
            ret = self.getImpl().get_jobs(self.getContext(), {'job_ids': []})
        except Exception as ex:
            #    traceback.print_tb(ex)
           self.assertTrue(False, 'Did not expect an exception: ' + str(ex))
           return

        self.assertIsInstance(ret, list)
        result = ret[0]
        self.assertIsInstance(result, dict)
        self.assertIn('jobs', result)
        jobs = result.get('jobs')
        self.assertIsInstance(jobs, list)
        self.assertEqual(len(jobs), 0)
