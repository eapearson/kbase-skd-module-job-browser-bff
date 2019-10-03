from JobBrowserBFF.TestBase import TestBase

class JobBrowserBFFTest(TestBase):
    def test_get_job_types_happy(self):
        try:
            ret = self.getImpl().get_job_types(self.getContext())
        except Exception as ex:
           self.assertTrue(False, 'Did not expect an exception: ' + str(ex.message))
           return

        self.assertIsInstance(ret, list)
        result = ret[0]
        self.assertIsInstance(result, dict)
        self.assertIn('job_types', result)
        job_types = result.get('job_types')
        self.assertIsInstance(job_types, list)
        self.assertEqual(len(job_types), 3)
        job_type = job_types[0]
        self.assertEqual(job_type['code'], 'narrative')
