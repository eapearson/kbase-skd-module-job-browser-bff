from JobBrowserBFF.TestBase import TestBase

# The env and user don't really matter, though.
ENV='mock'
USER_CLASS = 'user'

class JobBrowserBFFTest(TestBase):
    def test_get_job_types_happy(self):
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.get_job_types(context)
            self.assertIsInstance(ret, list)
            result = ret[0]
            self.assertIsInstance(result, dict)
            self.assertIn('job_types', result)
            job_types = result.get('job_types')
            self.assertIsInstance(job_types, list)
            self.assertEqual(len(job_types), 3)
            job_type = job_types[0]
            self.assertEqual(job_type['code'], 'narrative')
        except Exception as ex:
           self.assert_no_exception(ex)
