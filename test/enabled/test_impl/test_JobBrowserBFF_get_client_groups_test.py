from JobBrowserBFF.TestBase import TestBase

UPSTREAM_SERVICE = 'ee2'
ENV = 'ci'
USER_CLASS = 'user'


class JobBrowserBFFTest(TestBase):
    def test_get_client_groups_happy(self):
        try:
            self.set_config('upstream-service', UPSTREAM_SERVICE)
            impl, context = self.impl_for(ENV, USER_CLASS)
            result = impl.get_client_groups(context)
            self.assertIsInstance(result, dict)
            self.assertIn('client_groups', result)
            client_groups = result.get('client_groups')
            self.assertIsInstance(client_groups, list)
        except Exception as ex:
            self.assert_no_exception(ex)
