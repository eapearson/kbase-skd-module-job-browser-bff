from http.server import BaseHTTPRequestHandler,HTTPServer
import json
import time
import importlib
import inspect

def class_for_name(module_name, class_name):
    # load the module, will raise ImportError if module cannot be loaded
    m = __import__(module_name, globals(), locals(), [class_name])
    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, class_name)
    return c

class JSONRPCHandler(BaseHTTPRequestHandler):

    def send_server_error(self, response_code, message):
        self.send_response(response_code)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(bytes(message))

    def send_json_response(self, id, value):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        data = {
            'id': id,
            'version': '1.1',
            'result': value
        }
        self.wfile.write(bytes(json.dumps(data)))

    def send_error_response(self, id, value):
        self.send_response(500)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        data = {
            'id': id,
            'version': '1.1',
            'error': value
        }
        self.wfile.write(bytes(json.dumps(data)))

    def send_as_response(self, content_type, value):
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(bytes(value))

    def send_json_string_response(self, value):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(value))

    def validate_input(self, input):
        # convert to json
        input_json = json.loads(input)

        # validate struct
        if not isinstance(input_json, dict):
            raise ValueError('Invalid input structure')

        if 'version' not in input_json:
            raise ValueError('Missing params field "version"')

        version = input_json['version']
        if version != '1.1':
            raise ValueError('Invalid version; expected "1.1", got "%s"' % (version))
            
        if 'id' not in input_json:
            raise ValueError('Missing params field "id"')

        id = input_json['id']

        if 'method' not in input_json:
            raise ValueError('Missing "method" field')

        module, method = input_json['method'].split('.')
        
        if 'params' not in input_json:
            raise ValueError('Missing "params" field')

        params = input_json['params']
        if not isinstance(params, list):
            raise ValueError('The "params" field must be list')

        return version, id, module, method, params

    def do_QUIT(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write('Quitting Mock Server...')
        self.server.stop = True

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self.send_server_error(501, 'GET is not supported for JSON-RPC')

    def do_POST(self):
        # is json?
        content_type = self.headers.get('Content-Type', None)
        if content_type is None:
            self.send_error(500, 'Sorry, Content-Type must be supplied')
            return

        if content_type != 'application/json':
            self.send_error(500, 'Sorry, Content-Type must be application/json')
            return

        # read input
        input_length = int(self.headers.get('Content-Length'))
        input = self.rfile.read(input_length)

        version, id, module, method, params = self.validate_input(input)

        # response_json = {
        #     'message': 'Sorry, just testing...',
        #     'version': version,
        #     'id': id,
        #     'module': module,
        #     'method': method,
        #     'params': params
        # }
        # response = json.dumps(response_json)

        # find module, or not
        try:
            servers_module = importlib.import_module('MockServers.Servers')
            class_name = 'JSONRPC_' + module
            if not hasattr(servers_module, class_name):
                self.send_error(500, 'Cannot find server class "%s"' % class_name)
                return
            module_class = getattr(servers_module, class_name)
            if not inspect.isclass(module_class):
                self.send_error(500, 'RPC module is not a class "%s"' % class_name)
                return 
            # 
            # module_class = class_for_name('MockServers.Servers', module)
        except Exception as err:
            self.send_error(500, 'Cannot load service module "%s": %s' % (module, err.message))
            return


        # look up method
        svc = module_class()
        if not svc.is_method(method):
            self.send_error(500, 'Method not supported: "%s"' % method)
            return

        # call method
        try:
            self.log_message('CALLING %s, %s', method, params)
            response_json, error, debug = svc.call_method(method, params)
        except Exception as err:
            self.send_error_response(500, {
                'name': 'Error processing method',
                'code': -32000,
                'message': 'Error running method "%s": %s' % (method, err.message),
                'data': None
            })
            return
          
        if debug:
            if debug.get('send-as', False):
                self.send_as_response(debug['send-as'], response_json)
            elif debug.get('send-as-json-string', False):
                self.send_json_string_response(response_json)
            else: 
                self.send_error(500, 'Bad debug %s' % (str(debug)))
        elif error:
            self.log_message('error response %s', error)
            self.send_error_response(500, error)
        else:
            # return json or error
            self.log_message('success response %s', response_json)
            self.send_json_response(id, response_json)


# class MockServer(BaseHTTPServer.HTTPServer):
#     # def __init__(self, host, port):
#     #     self.host = host
#     #     self.port = port
#     #     self.stop = False

#     def serve_forever(self):
#         self.stop = False
#         while not self.stop:
#             self.handle_request()

class ServerController(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.httpd = None

    def start(self):
        self.httpd = HTTPServer((self.host, self.port), JSONRPCHandler)

        # server_class = MockServer
        # handler_class = JSONRPCHandler
        # self.httpd = server_class((self.host, self.port), handler_class)
        print(time.asctime(), 'JSON RPC Server Starting at %s:%s' % (self.host, self.port))
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        # self.httpd.server_close()

    def stop(self):
        self.httpd.server_close()
        print(time.asctime(), 'JSON RPC Server Stopped at %s:%s' % (self.host, self.port))