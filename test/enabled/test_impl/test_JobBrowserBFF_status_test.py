from JobBrowserBFF.TestBase import TestBase

UPSTREAM_SERVICE = 'ee2'
ENV = 'ci'
USER_CLASS = 'user'


class JobBrowserBFFTest(TestBase):
    def test_status_happy(self):
        try:
            self.set_config('upstream-service', UPSTREAM_SERVICE)
            impl, context = self.impl_for(ENV, USER_CLASS)
            result = impl.status(context)
            self.assertIsInstance(result, dict)
            self.assertIn('state', result)
            self.assertEqual(result['state'], 'OK')
        except Exception as ex:
            self.assert_no_exception(ex)
