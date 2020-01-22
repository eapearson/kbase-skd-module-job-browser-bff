from JobBrowserBFF.TestBase import TestBase

# The env and user don't really matter, though.
ENV='mock'
USER_CLASS = 'user'

class JobBrowserBFFTest(TestBase):
    def test_get_sort_specs_happy(self):
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.get_sort_specs(context)
            self.assertIsInstance(ret, list)
            result = ret[0]
            self.assertIsInstance(result, dict)
            self.assertIn('sort_specs', result)
            sort_specs = result.get('sort_specs')
            self.assertIsInstance(sort_specs, list)
        except Exception as ex:
           self.assert_no_exception(ex)
