from JobBrowserBFF.TestBase import TestBase

# The env and user don't really matter, though.
ENV='mock'
USER_CLASS='user'

class JobBrowserBFFTest(TestBase):
    def test_get_job_states_happy(self):
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.get_job_states(context)
            self.assertIsInstance(ret, list)
            result = ret[0]
            self.assertIsInstance(result, dict)
            self.assertIn('job_states', result)
            job_states = result.get('job_states')
            self.assertIsInstance(job_states, list)
            self.assertEqual(len(job_states), 7)
            job_type = job_states[0]
            self.assertEqual(job_type['code'], 'queued')
        except Exception as ex:
           self.assert_no_exception(ex)
