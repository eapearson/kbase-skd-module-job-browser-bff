import time


class JSONRPCBase(object):
    def is_method(self, method_name):
        if not hasattr(self, 'do_' + method_name):
            return False
        method = getattr(self, 'do_' + method_name)
        return callable(method)

    def call_method(self, method_name, params):
        return getattr(self, 'do_' + method_name)(params)


class JSONRPC_Test(JSONRPCBase):
    def do_status(self, params):
        return [{
            'state': 'ok'
        }], None, None

    def do_trigger_500(self, params):
        raise ValueError('This is a 500 response')

    def do_non_json_response(self, params):
        return 'This is not JSON!', None, {
            'send-as-json-string': True
        }

    def do_incorrect_content_type(self, params):
        return 'This is json, but the content type is wrong', None, {
            'send-as': 'text/plain'
        }

    def do_return_non_list(self, params):
        return {
            'message': 'This is not a list...'
        }, None, None

    def do_sleep_for(self, params):
        start = time.time()
        time.sleep(params[0]['sleep'])
        elapsed = time.time() - start
        return {
            'slept_for': elapsed
        }, None, None

    # TODO: trigger for all JSON RPC 2.0 errors, using the standard
    # structure (dict).


class JSONRPC_ServiceWizard(JSONRPCBase):
    def __init__(self):
        super(JSONRPC_ServiceWizard, self).__init__()
        self.modules = {
            'Test': {
                'url': 'http://localhost:5001'
            },
            'kb_Metrics': {
                'url': 'http://localhost:5001'
            }
        }

    def do_get_service_status(self, params):
        module_name = params[0].get('module_name')
        # version = params[0].get('version', None)

        module = self.modules.get(module_name, None)
        if module is None:
            return None, {
                'name': 'Module not found',
                'code': -32601,
                'message': 'Could not find module "%s"' % (module_name),
                'data': None
            }, None

        return [module], None, None
