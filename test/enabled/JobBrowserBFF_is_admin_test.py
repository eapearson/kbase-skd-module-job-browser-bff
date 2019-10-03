from JobBrowserBFF.TestBase import TestBase

class JobBrowserBFFTest(TestBase):
    def test_is_admin_happy(self):
        try:
            ret = self.getImpl().is_admin(self.getContext())
        except Exception as ex:
           self.assertTrue(False, 'Did not expect an exception: ' + str(ex.message))
           return

        self.assertIsInstance(ret, list)

        result = ret[0]
        self.assertIsInstance(result, dict)
        self.assertIn('is_admin', result)
        is_admin = result.get('is_admin')
        self.assertIsInstance(is_admin, bool)
        self.assertEqual(is_admin, True)
