from JobBrowserBFF.TestBase import TestBase

UPSTREAM_SERVICE = 'ee2'
ENV = 'ci'
USER_CLASS = 'user'


class JobBrowserBFFTest(TestBase):
    def test_get_searchable_job_fields_happy(self):
        try:
            self.set_config('upstream-service', UPSTREAM_SERVICE)
            impl, context = self.impl_for(ENV, USER_CLASS)
            result = impl.get_searchable_job_fields(context)
            self.assertIsInstance(result, dict)
            self.assertIn('searchable_job_fields', result)
            searchable_job_fields = result.get('searchable_job_fields')
            self.assertIsInstance(searchable_job_fields, list)
        except Exception as ex:
            self.assert_no_exception(ex)
