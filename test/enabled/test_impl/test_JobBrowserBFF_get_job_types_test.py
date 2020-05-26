from JobBrowserBFF.TestBase import TestBase

UPSTREAM_SERVICE = 'ee2'
ENV = 'ci'
USER_CLASS = 'user'


class JobBrowserBFFTest(TestBase):
    def test_get_job_types_happy(self):
        try:
            self.set_config('upstream-service', UPSTREAM_SERVICE)
            impl, context = self.impl_for(ENV, USER_CLASS)
            result = impl.get_job_types(context)
            self.assertIsInstance(result, dict)
            self.assertIn('job_types', result)
            job_types = result.get('job_types')
            self.assertIsInstance(job_types, list)
            self.assertEqual(len(job_types), 3)
            job_type = job_types[0]
            self.assertEqual(job_type['code'], 'narrative')
        except Exception as ex:
            self.assert_no_exception(ex)
