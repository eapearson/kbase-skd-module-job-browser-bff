from JobBrowserBFF.TestBase import TestBase

UPSTREAM_SERVICE = 'ee2'
ENV = 'ci'
USER_CLASS = 'user'


class JobBrowserBFFTest(TestBase):
    def test_get_sort_specs_happy(self):
        try:
            self.set_config('upstream-service', UPSTREAM_SERVICE)
            impl, context = self.impl_for(ENV, USER_CLASS)
            result = impl.get_sort_specs(context)
            self.assertIsInstance(result, dict)
            self.assertIn('sort_specs', result)
            sort_specs = result.get('sort_specs')
            self.assertIsInstance(sort_specs, list)
        except Exception as ex:
            self.assert_no_exception(ex)
