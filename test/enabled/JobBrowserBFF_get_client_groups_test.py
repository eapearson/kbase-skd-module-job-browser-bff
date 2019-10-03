from JobBrowserBFF.TestBase import TestBase

class JobBrowserBFFTest(TestBase):
    def test_get_client_groups_happy(self):
        try:
            ret = self.getImpl().get_client_groups(self.getContext())
        except Exception as ex:
           self.assertTrue(False, 'Did not expect an exception: ' + str(ex.message))
           return

        self.assertIsInstance(ret, list)
        result = ret[0]
        self.assertIsInstance(result, dict)
        self.assertIn('client_groups', result)
        client_groups = result.get('client_groups')
        self.assertIsInstance(client_groups, list)
       