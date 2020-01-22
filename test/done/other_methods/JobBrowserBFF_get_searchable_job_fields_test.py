from JobBrowserBFF.TestBase import TestBase

# The env and user don't really matter, though.
ENV='mock'
USER_CLASS = 'user'

class JobBrowserBFFTest(TestBase):
    def test_get_searchable_job_fields_happy(self):
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.get_searchable_job_fields(context)
            self.assertIsInstance(ret, list)
            result = ret[0]
            self.assertIsInstance(result, dict)
            self.assertIn('searchable_job_fields', result)
            searchable_job_fields = result.get('searchable_job_fields')
            self.assertIsInstance(searchable_job_fields, list)
        except Exception as ex:
           self.assert_no_exception(ex)
