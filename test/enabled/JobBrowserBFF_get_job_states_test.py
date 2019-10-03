from JobBrowserBFF.TestBase import TestBase

class JobBrowserBFFTest(TestBase):
    def test_get_job_states_happy(self):
        try:
            ret = self.getImpl().get_job_states(self.getContext())
        except Exception as ex:
           self.assertTrue(False, 'Did not expect an exception: ' + str(ex.message))
           return

        self.assertIsInstance(ret, list)
        result = ret[0]
        self.assertIsInstance(result, dict)
        self.assertIn('job_states', result)
        job_states = result.get('job_states')
        self.assertIsInstance(job_states, list)
        self.assertEqual(len(job_states), 7)
        job_type = job_states[0]
        self.assertEqual(job_type['code'], 'queued')
