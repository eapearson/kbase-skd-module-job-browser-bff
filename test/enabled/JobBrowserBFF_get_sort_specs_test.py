from JobBrowserBFF.TestBase import TestBase

class JobBrowserBFFTest(TestBase):
    def test_get_sort_specs_happy(self):
        try:
            ret = self.getImpl().get_sort_specs(self.getContext())
        except Exception as ex:
           self.assertTrue(False, 'Did not expect an exception: ' + str(ex.message))
           return

        self.assertIsInstance(ret, list)

        result = ret[0]
        self.assertIsInstance(result, dict)
        self.assertIn('sort_specs', result)
        sort_specs = result.get('sort_specs')
        self.assertIsInstance(sort_specs, list)
