from JobBrowserBFF.TestBase import TestBase

UPSTREAM_SERVICE = 'ee2'
ENV = 'ci'
USER_CLASS = 'user'


class JobBrowserBFFTest(TestBase):
    def test_get_log_levels_happy(self):
        try:
            self.set_config('upstream-service', UPSTREAM_SERVICE)
            impl, context = self.impl_for(ENV, USER_CLASS)
            result = impl.get_log_levels(context)
            self.assertIsInstance(result, dict)
            self.assertIn('log_levels', result)
            log_levels = result.get('log_levels')
            self.assertIsInstance(log_levels, list)
        except Exception as ex:
            self.assert_no_exception(ex)
