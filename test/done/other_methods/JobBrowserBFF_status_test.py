from JobBrowserBFF.TestBase import TestBase

# The env and user don't really matter, though.
ENV='mock'
USER_CLASS='user'

class JobBrowserBFFTest(TestBase):
    def test_status_happy(self):
        try:
            
            impl, context = self.impl_for(ENV, USER_CLASS)
            ret = impl.status(context)
            self.assertIsInstance(ret, list)
            result = ret[0]
            self.assertIsInstance(result, dict)
            self.assertIn('state', result)
            self.assertEqual(result['state'], 'OK')
        except Exception as ex:
           self.assert_no_exception(ex)

       