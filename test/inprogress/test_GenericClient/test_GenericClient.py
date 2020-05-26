from biokbase.GenericClient import GenericClient
from biokbase.Errors import ServiceError
from JobBrowserBFF.TestBase import TestBase

MOCK_SERVER_URL = 'http://localhost:5001'
CALL_TIMEOUT = 5


class GeneriClientTess(TestBase):

    def test_basic_constructor(self):
        GenericClient(module='Foo',
                      url='https://example.kbase.us',
                      token='FAKE',
                      timeout=CALL_TIMEOUT)
        self.assertEqual(True, True)

    def test_constructor_missing_module(self):
        with self.assertRaisesRegexp(ValueError, 'module'):
            GenericClient(url='https://example.kbase.us',
                          token='FAKE',
                          timeout=CALL_TIMEOUT)

    def test_constructor_missing_url(self):
        with self.assertRaisesRegexp(ValueError, 'url'):
            GenericClient(module='Foo',
                          token='FAKE',
                          timeout=CALL_TIMEOUT)

    def test_constructor_missing_timeout(self):
        with self.assertRaisesRegexp(ValueError, 'timeout'):
            GenericClient(module='Foo',
                          url='https://example.kbase.us',
                          token='FAKE')

    def test_mock_call_status(self):
        client = GenericClient(module='Test',
                               url='http://localhost:5001',
                               token='FAKE',
                               timeout=CALL_TIMEOUT)
        result = client.call_func('status')
        self.assertIn('state', result)
        self.assertEqual(result['state'], 'ok')

    def test_mock_call_timeout(self):
        TIMEOUT = 1
        client = GenericClient(module='Test',
                               url='http://localhost:5001',
                               token='FAKE',
                               timeout=TIMEOUT)
        with self.assertRaises(ServiceError) as context_manager:
            client.call_func('sleep_for', {'sleep': 2})

        service_error = context_manager.exception
        self.assertEqual(service_error.code, 100)
