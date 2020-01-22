import requests
import json
import uuid
import urllib3

from biokbase.Errors import ServiceError

class GenericClient(object):
    def __init__(self, module=None, url=None, token=None, timeout=None):
        if module is None:
            raise ValueError('The "module" argument is required')
        if url is None:
            raise ValueError('The "url" argument is required')
        if timeout is None:
            raise ValueError('The "timeout" argument is required')

        self.module = module
        self.token = token
        self.url = url
        # Note that we operate with ms time normally, but requests uses
        # seconds float.
        self.timeout = timeout

    def get_timeout(self, timeout):
        timeout = timeout or self.timeout
        return timeout / 1000

    def call_func(self, func_name, params=None, timeout=None):
        if not isinstance(func_name, str):
            raise ValueError('"func_name" must be a string')

        if params is None:
            wrapped_params = []
        else:
            wrapped_params = [params]

        call_params = {
            'id': str(uuid.uuid4()),
            'method': self.module + '.' + func_name,
            'version': '1.1',
            'params': wrapped_params
        }

        header = {
            'Content-Type': 'application/json'
        }
        if self.token:
            header['Authorization'] = self.token

        timeout = self.get_timeout(timeout)
        try:
            r = requests.post(self.url, headers=header, data=json.dumps(call_params), timeout=timeout)
        except requests.exceptions.ReadTimeout as rte:
            raise ServiceError(
                code=100,
                message='Timeout calling service endpoint',
                data={
                    'url': self.url,
                    'headers': header,
                    'timeout': timeout
                })
        except Exception as ex:
            raise ServiceError(code=100, message='Error calling service endpoint: ' + ex.message,
                data={
                    'url': self.url,
                    'headers': header,                    
                })

        if r.headers.get('content-type', '').startswith('application/json'):
            try:
                response = r.json()
            except Exception as err:
                raise ValueError('Invalid response; claiming to be json, but not: %s' % err.message)
            
            error = response.get('error')
            if error:
                # Better be a JSON RPC 2.0 Error structure
                # TODO: adjust to improved service error.
                error_data = {
                    'stack': error.get('error'),
                    'name': error.get('name')
                }
                raise ServiceError(
                    code=error.get('code'),
                    message=error.get('message', error.get('name')),
                    data=error_data)

            result = response.get('result')

            if isinstance(result, list):
                return result[0]
            elif result is None:
                return result
            else:
                raise ValueError('Expected result to be array or null, is ' + type(result).__name__)

        r.raise_for_status()
        raise ValueError('Invalid response; not json, not an error status')