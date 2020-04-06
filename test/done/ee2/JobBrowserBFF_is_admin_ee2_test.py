from JobBrowserBFF.TestBase import TestBase
# import unittest

UPSTREAM_SERVICE = 'ee2'
ENV = 'ci'
USER_CLASS = 'admin'


class JobBrowserBFFTest(TestBase):
    # Uncomment to skip this test
    # @unittest.skip("skipped test_is_admin_happy")
    def test_is_admin_happy(self):
        try:
            self.set_config('upstream-service', UPSTREAM_SERVICE)
            impl, context = self.impl_for(ENV, USER_CLASS)

            ret = impl.is_admin(context)

            self.assertIsInstance(ret, list)
            result = ret[0]
            self.assertIsInstance(result, dict)
            self.assertIn('is_admin', result)
            is_admin = result.get('is_admin')
            self.assertIsInstance(is_admin, bool)
            self.assertEqual(is_admin, True)
        except Exception as ex:
            self.assert_no_exception(ex)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_is_admin_happy")
    def test_is_not_admin_happy(self):
        try:
            self.set_config('upstream-service', UPSTREAM_SERVICE)

            impl, context = self.impl_for(ENV, 'user')

            ret = impl.is_admin(context)

            self.assertIsInstance(ret, list)
            result = ret[0]
            self.assertIsInstance(result, dict)
            self.assertIn('is_admin', result)
            is_admin = result.get('is_admin')
            self.assertIsInstance(is_admin, bool)
            self.assertEqual(is_admin, False)
        except Exception as ex:
            self.assert_no_exception(ex)
