from JobBrowserBFF.TestBase import TestBase

# The env and user don't really matter, though.
UPSTREAM_SERVICE = 'ee2'
ENV = 'ci'
USER_CLASS = 'user'


class JobBrowserBFFTest(TestBase):
    def test_get_job_states_happy(self):
        try:
            self.set_config('upstream-service', UPSTREAM_SERVICE)
            impl, context = self.impl_for(ENV, USER_CLASS)
            result = impl.get_job_states(context)
            self.assertIsInstance(result, dict)
            self.assertIn('job_states', result)
            job_states = result.get('job_states')
            self.assertIsInstance(job_states, list)
            self.assertEqual(len(job_states), 7)
            job_type = job_states[0]
            self.assertEqual(job_type['code'], 'queued')
        except Exception as ex:
            self.assert_no_exception(ex)
