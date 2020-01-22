from JobBrowserBFF.TestBase import TestBase

# The env and user don't really matter, though.
ENV='mock'
USER_CLASS = 'user'

class JobBrowserBFFTest(TestBase):
    def test_get_log_levels_happy(self):
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.get_log_levels(context)
            self.assertIsInstance(ret, list)
            result = ret[0]
            self.assertIsInstance(result, dict)
            self.assertIn('log_levels', result)
            log_levels = result.get('log_levels')
            self.assertIsInstance(log_levels, list)
        except Exception as ex:
           self.assert_no_exception(ex)
