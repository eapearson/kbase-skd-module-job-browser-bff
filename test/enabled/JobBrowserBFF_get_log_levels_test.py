from JobBrowserBFF.TestBase import TestBase

class JobBrowserBFFTest(TestBase):
    def test_get_log_levels_happy(self):
        try:
            ret = self.getImpl().get_log_levels(self.getContext())
        except Exception as ex:
           self.assertTrue(False, 'Did not expect an exception: ' + str(ex.message))
           return

        self.assertIsInstance(ret, list)

        result = ret[0]
        self.assertIsInstance(result, dict)
        self.assertIn('log_levels', result)
        log_levels = result.get('log_levels')
        self.assertIsInstance(log_levels, list)
