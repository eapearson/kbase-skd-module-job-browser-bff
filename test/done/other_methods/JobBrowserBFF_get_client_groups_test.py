from JobBrowserBFF.TestBase import TestBase

# The env and user don't really matter, though.
ENV='mock'
USER_CLASS='user'

class JobBrowserBFFTest(TestBase):
    def test_get_client_groups_happy(self):
        try:
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.get_client_groups(context)
            self.assertIsInstance(ret, list)
            result = ret[0]
            self.assertIsInstance(result, dict)
            self.assertIn('client_groups', result)
            client_groups = result.get('client_groups')
            self.assertIsInstance(client_groups, list)
        except Exception as ex:
           self.assert_no_exception(ex)

       