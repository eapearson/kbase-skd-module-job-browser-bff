from JobBrowserBFF.TestBase import TestBase
import JobBrowserBFF.Utils as utils

UPSTREAM_SERVICE = 'ee2'
ENV = 'ci'
USER_CLASS = 'user'


class UtilsTest(TestBase):
    def test_parse_app_id(self):
        cases = [
            {
                'input': ['foo/bar', None],
                'output': {
                    'id': 'foo/bar',
                    'module_name': 'foo',
                    'function_name': 'bar',
                    'type': 'narrative'
                }
            },
            {
                'input': ['foo/bar/', None],
                'output': {
                    'id': 'foo/bar',
                    'module_name': 'foo',
                    'function_name': 'bar',
                    'type': 'narrative'
                }
            },
            {
                'input': [None, 'foo.bar'],
                'output': {
                    'id': 'foo/bar',
                    'module_name': 'foo',
                    'function_name': 'bar',
                    'type': 'other'
                }
            },
            {
                'input': [None, None],
                'output': None
            },
            {
                'input': ['foo', None],
                'output': None
            },
            {
                'input': ['foo/bar/baz', None],
                'output': None
            },
            {
                'input': ['foo/bar/baz/bing', None],
                'output': None
            }
        ]
        try:
            for case in cases:
                result = utils.parse_app_id(*case['input'])
                # print('RESULT', result)
                self.assertEqual(result, case['output'])
        except Exception as ex:
            self.assert_no_exception(ex)
