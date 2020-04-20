#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import json
import os
import random as _random
import sys
import traceback
from getopt import getopt, GetoptError
from multiprocessing import Process
from os import environ
from wsgiref.simple_server import make_server

import requests as _requests
from jsonrpcbase import JSONRPCService, InvalidParamsError, KeywordError, \
    JSONRPCError, InvalidRequestError
from jsonrpcbase import ServerError as JSONServerError

from biokbase import log
from JobBrowserBFF.authclient import KBaseAuth as _KBaseAuth

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

DEPLOY = 'KB_DEPLOYMENT_CONFIG'
SERVICE = 'KB_SERVICE_NAME'
AUTH = 'auth-service-url'

# Note that the error fields do not match the 2.0 JSONRPC spec


def get_config_file():
    return environ.get(DEPLOY, None)


def get_service_name():
    return environ.get(SERVICE, None)


def get_config():
    if not get_config_file():
        return None
    retconfig = {}
    config = ConfigParser()
    config.read(get_config_file())
    for nameval in config.items(get_service_name() or 'JobBrowserBFF'):
        retconfig[nameval[0]] = nameval[1]
    return retconfig


config = get_config()

from JobBrowserBFF.JobBrowserBFFImpl import JobBrowserBFF  # noqa @IgnorePep8
impl_JobBrowserBFF = JobBrowserBFF(config)


class JSONObjectEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, frozenset):
            return list(obj)
        if hasattr(obj, 'toJSONable'):
            return obj.toJSONable()
        return json.JSONEncoder.default(self, obj)


class JSONRPCServiceCustom(JSONRPCService):

    def call(self, ctx, jsondata):
        """
        Calls jsonrpc service's method and returns its return value in a JSON
        string or None if there is none.

        Arguments:
        jsondata -- remote method call in jsonrpc format
        """
        result = self.call_py(ctx, jsondata)
        if result is not None:
            return json.dumps(result, cls=JSONObjectEncoder)

        return None

    def _call_method(self, ctx, request):
        """Calls given method with given params and returns it value."""
        method = self.method_data[request['method']]['method']
        params = request['params']
        result = None
        try:
            if isinstance(params, list):

                # Does it have enough arguments?
                if len(params) < self._man_args(method) - 1:
                    raise InvalidParamsError(data={'issue': 'not enough arguments'})

                # Does it have too many arguments?
                if(not self._vargs(method) and len(params) >
                        self._max_args(method) - 1):
                    raise InvalidParamsError(data={'issue': 'too many arguments'})

                result = method(ctx, *params)
            elif isinstance(params, dict):
                # Do not accept keyword arguments if the jsonrpc version is
                # not >=2.0
                if request['jsonrpc'] < 20:
                    raise KeywordError

                result = method(ctx, **params)
            else:  # No params
                result = method(ctx)
        except JSONRPCError:
            raise
        except Exception as e:
            # log.exception('method %s threw an exception' % request['method'])
            # Exception was raised inside the method.
            newerr = JSONServerError()
            newerr.trace = traceback.format_exc()
            if len(e.args) == 1:
                newerr.data = repr(e.args[0])
            else:
                newerr.data = repr(e.args)
            raise newerr
        return result

    def call_py(self, ctx, jsondata):
        """
        Calls jsonrpc service's method and returns its return value in python
        object format or None if there is none.

        This method is same as call() except the return value is a python
        object instead of JSON string. This method is mainly only useful for
        debugging purposes.
        """
        rdata = jsondata
        # we already deserialize the json string earlier in the server code, no
        # need to do it again
#        try:
#            rdata = json.loads(jsondata)
#        except ValueError:
#            raise ParseError

        # set some default values for error handling
        request = self._get_default_vals()

        if isinstance(rdata, dict) and rdata:
            # It's a single request.
            self._fill_request(request, rdata)
            respond = self._handle_request(ctx, request)

            # Don't respond to notifications
            if respond is None:
                return None

            return respond
        elif isinstance(rdata, list) and rdata:
            # It's a batch.
            requests = []
            responds = []

            for rdata_ in rdata:
                # set some default values for error handling
                request_ = self._get_default_vals()
                self._fill_request(request_, rdata_)
                requests.append(request_)

            for request_ in requests:
                respond = self._handle_request(ctx, request_)
                # Don't respond to notifications
                if respond is not None:
                    responds.append(respond)

            if responds:
                return responds

            # Nothing to respond.
            return None
        else:
            # empty dict, list or wrong type
            raise InvalidRequestError

    def _handle_request(self, ctx, request):
        """Handles given request and returns its response."""
        if 'types' in self.method_data[request['method']]:
            self._validate_params_types(request['method'], request['params'])

        result = self._call_method(ctx, request)

        # Do not respond to notifications.
        if request['id'] is None:
            return None

        respond = {}
        self._fill_ver(request['jsonrpc'], respond)
        respond['result'] = result
        respond['id'] = request['id']

        return respond


class MethodContext(dict):

    def __init__(self, logger):
        self['client_ip'] = None
        self['user_id'] = None
        self['authenticated'] = None
        self['token'] = None
        self['module'] = None
        self['method'] = None
        self['call_id'] = None
        self['rpc_context'] = None
        self._debug_levels = set([7, 8, 9, 'DEBUG', 'DEBUG2', 'DEBUG3'])
        self._logger = logger

    def log_err(self, message):
        self._log(log.ERR, message)

    def log_info(self, message):
        self._log(log.INFO, message)

    def log_debug(self, message, level=1):
        if level in self._debug_levels:
            pass
        else:
            level = int(level)
            if level < 1 or level > 3:
                raise ValueError("Illegal log level: " + str(level))
            level = level + 6
        self._log(level, message)

    def set_log_level(self, level):
        self._logger.set_log_level(level)

    def get_log_level(self):
        return self._logger.get_log_level()

    def clear_log_level(self):
        self._logger.clear_user_log_level()

    def _log(self, level, message):
        self._logger.log_message(level, message, self['client_ip'],
                                 self['user_id'], self['module'],
                                 self['method'], self['call_id'])


class ServerError(Exception):
    '''
    The call returned an error. Fields:
    name - the name of the error.
    code - the error code.
    message - a human readable error message.
    data - the server side stacktrace.
    '''

    def __init__(self, name, code, message, data=None, error=None):
        super(Exception, self).__init__(message)
        self.name = name
        self.code = code
        self.message = message if message else ''
        if data:
            self.data = data
        elif error:
            self.data = {
                'error': error
            }

    def __str__(self):
        return self.name + ': ' + str(self.code) + '. ' + self.message + \
            '\n' + self.data


def getIPAddress(environ):
    xFF = environ.get('HTTP_X_FORWARDED_FOR')
    realIP = environ.get('HTTP_X_REAL_IP')
    trustXHeaders = config is None or \
        config.get('dont_trust_x_ip_headers') != 'true'

    if (trustXHeaders):
        if (xFF):
            return xFF.split(',')[0].strip()
        if (realIP):
            return realIP.strip()
    return environ.get('REMOTE_ADDR')


class Application(object):
    # Wrap the wsgi handler in a class definition so that we can
    # do some initialization and avoid regenerating stuff over
    # and over

    def logcallback(self):
        self.serverlog.set_log_file(self.userlog.get_log_file())

    def log(self, level, context, message):
        self.serverlog.log_message(level, message, context['client_ip'],
                                   context['user_id'], context['module'],
                                   context['method'], context['call_id'])

    def __init__(self):
        submod = get_service_name() or 'JobBrowserBFF'
        self.userlog = log.log(
            submod, ip_address=True, authuser=True, module=True, method=True,
            call_id=True, changecallback=self.logcallback,
            config=get_config_file())
        self.serverlog = log.log(
            submod, ip_address=True, authuser=True, module=True, method=True,
            call_id=True, logfile=self.userlog.get_log_file())
        self.serverlog.set_log_level(6)
        self.rpc_service = JSONRPCServiceCustom()
        self.method_authentication = dict()
        self.rpc_service.add(impl_JobBrowserBFF.get_jobs,
                             name='JobBrowserBFF.get_jobs',
                             types=[dict])
        self.method_authentication['JobBrowserBFF.get_jobs'] = 'required'  # noqa
        self.rpc_service.add(impl_JobBrowserBFF.query_jobs,
                             name='JobBrowserBFF.query_jobs',
                             types=[dict])
        self.method_authentication['JobBrowserBFF.query_jobs'] = 'required'  # noqa
        self.rpc_service.add(impl_JobBrowserBFF.get_job_log,
                             name='JobBrowserBFF.get_job_log',
                             types=[dict])
        self.method_authentication['JobBrowserBFF.get_job_log'] = 'required'  # noqa
        self.rpc_service.add(impl_JobBrowserBFF.cancel_job,
                             name='JobBrowserBFF.cancel_job',
                             types=[dict])
        self.method_authentication['JobBrowserBFF.cancel_job'] = 'required'  # noqa
        self.rpc_service.add(impl_JobBrowserBFF.get_job_types,
                             name='JobBrowserBFF.get_job_types',
                             types=[])
        self.method_authentication['JobBrowserBFF.get_job_types'] = 'required'  # noqa
        self.rpc_service.add(impl_JobBrowserBFF.get_job_states,
                             name='JobBrowserBFF.get_job_states',
                             types=[])
        self.method_authentication['JobBrowserBFF.get_job_states'] = 'required'  # noqa
        self.rpc_service.add(impl_JobBrowserBFF.get_client_groups,
                             name='JobBrowserBFF.get_client_groups',
                             types=[])
        self.method_authentication['JobBrowserBFF.get_client_groups'] = 'required'  # noqa
        self.rpc_service.add(impl_JobBrowserBFF.get_searchable_job_fields,
                             name='JobBrowserBFF.get_searchable_job_fields',
                             types=[])
        self.method_authentication['JobBrowserBFF.get_searchable_job_fields'] = 'required'  # noqa
        self.rpc_service.add(impl_JobBrowserBFF.get_sort_specs,
                             name='JobBrowserBFF.get_sort_specs',
                             types=[])
        self.method_authentication['JobBrowserBFF.get_sort_specs'] = 'required'  # noqa
        self.rpc_service.add(impl_JobBrowserBFF.get_log_levels,
                             name='JobBrowserBFF.get_log_levels',
                             types=[])
        self.method_authentication['JobBrowserBFF.get_log_levels'] = 'required'  # noqa
        self.rpc_service.add(impl_JobBrowserBFF.is_admin,
                             name='JobBrowserBFF.is_admin',
                             types=[])
        self.method_authentication['JobBrowserBFF.is_admin'] = 'required'  # noqa
        self.rpc_service.add(impl_JobBrowserBFF.status,
                             name='JobBrowserBFF.status',
                             types=[dict])
        authurl = config.get(AUTH) if config else None
        self.auth_client = _KBaseAuth(authurl)

    def handle_call(self, environ, ctx):
        try:
            body_size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            body_size = 0

        if environ['REQUEST_METHOD'] == 'OPTIONS':
            return '', None

        if body_size == 0:
            return None, self.process_error({
                'error': {
                    'code': -32700,
                    'message': "Parse error - no request data",
                }
            }, ctx)

        try:
            request_body = environ['wsgi.input'].read(body_size)
        except Exception as e:
            return None, self.process_error({
                'error': {
                    'code': -32603,
                    'message': 'Internal error',
                    'data': {
                        'exception': str(e)
                    }
                }
            }, ctx)

        try:
            request = json.loads(request_body)
        except ValueError as ve:
            return None, self.process_error({
                'error': {
                    'code': -32700,
                    'message': "Parse error - parsing the request as json",
                    'data': {
                        'exception': str(ve)
                    }
                }
            }, ctx)

        ctx['module'], ctx['method'] = request['method'].split('.')
        ctx['call_id'] = request['id']
        ctx['rpc_context'] = {
            'call_stack': [{
                'time': self.now_in_utc(),
                'method': request['method']
            }]
        }
        prov_action = {
            'service': ctx['module'],
            'method': ctx['method'],
            'method_params': request['params']
        }
        try:
            token = environ.get('HTTP_AUTHORIZATION')

            # Enforce authentication requirement.
            method_name = request['method']
            auth_req = self.method_authentication.get(method_name, 'none')
            if auth_req != 'none':
                if token is None and auth_req == 'required':
                    # TODO: replace with actual error return
                    err = JSONServerError()
                    err.data = (
                        'Authentication required for ' +
                        'JobBrowserBFF ' +
                        'but no authentication header was passed')
                    raise err
                elif token is None and auth_req == 'optional':
                    pass
                else:
                    try:
                        user = self.auth_client.get_user(token)
                        ctx['user_id'] = user
                        ctx['authenticated'] = 1
                        ctx['token'] = token
                    except Exception as e:
                        if auth_req == 'required':
                            err = JSONServerError()
                            err.data = \
                                "Token validation failed: %s" % e
                            raise err

            if (environ.get('HTTP_X_FORWARDED_FOR')):
                self.log(log.INFO, ctx, 'X-Forwarded-For: ' + environ.get('HTTP_X_FORWARDED_FOR'))

            self.log(log.INFO, ctx, 'start method')
            rpc_result = self.rpc_service.call(ctx, request)
            self.log(log.INFO, ctx, 'end method')
            if not rpc_result:
                return None, self.process_error({
                    'error': {
                        'code': -32001,
                        'message': 'Empty response from method'
                    }
                }, ctx, request)

            # TADA!
            return rpc_result, None
        except JSONRPCError as jre:
            response = {
                'error': {
                    'code': jre.code,
                    'message': jre.message,
                    'data': jre.data
                }
            }
            trace = jre.trace if hasattr(jre, 'trace') else None
            return None, self.process_error(response, ctx, request, trace)
        except Exception as ex:
            trace = ex.trace if hasattr(ex, 'trace') else None
            response = {
                'error': {
                    'code': -32000,
                    'message': 'Unexpected Server Error'
                }
            }
            return None, self.process_error(response, ctx, request, trace)

    def __call__(self, environ, start_response):
        ctx = MethodContext(self.userlog)
        ctx['client_ip'] = getIPAddress(environ)

        result, error = self.handle_call(environ, ctx)
        if result is not None:
            response_body = result
            status = '200 OK'
        else:
            response_body = error
            status = '200 OK'

        # TODO: CORS should not be handled here! That should be an administrative
        #       decision at the proxy level.
        response_headers = [
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Headers', environ.get(
                'HTTP_ACCESS_CONTROL_REQUEST_HEADERS', 'authorization')),
            ('content-type', 'application/json'),
            ('content-length', str(len(response_body)))]
        start_response(status, response_headers)
        return [response_body.encode('utf8')]

    def process_error(self, response, context, request=None, trace=None):
        response['jsonrpc'] = '2.0'

        # If trace provided, log it.
        if trace:
            trace = trace.split('\n')[0:-1]
            self.log(log.ERR, context, trace)
            # TODO: trace down how 'data' is getting corrupted as a string...
            if 'data' not in response['error']:
                response['error']['data'] = {}
            elif not isinstance(response['error']['data'], dict):
                response['error']['data'] = {
                    'message': response['error']['data']
                }
            # print('type?', isinstance(response['error']['data'], dict), type(response['error']['data']))
            # print(response)
            response['error']['data']['trace'] = trace

        # Errors early in the processing phase before a valid request is
        # available will not have a jsonrpc request available.
        if request is None:
            response['id'] = None
        else:
            response['id'] = request['id']

        return json.dumps(response)

    def now_in_utc(self):
        # noqa Taken from http://stackoverflow.com/questions/3401428/how-to-get-an-isoformat-datetime-string-including-the-default-timezone @IgnorePep8
        dtnow = datetime.datetime.now()
        dtutcnow = datetime.datetime.utcnow()
        delta = dtnow - dtutcnow
        hh, mm = divmod((delta.days * 24 * 60 * 60 + delta.seconds + 30) // 60,
                        60)
        return "%s%+02d:%02d" % (dtnow.isoformat(), hh, mm)


application = Application()

# This is the uwsgi application dictionary. On startup uwsgi will look
# for this dict and pull its configuration from here.
# This simply lists where to "mount" the application in the URL path
#
# This uwsgi module "magically" appears when running the app within
# uwsgi and is not available otherwise, so wrap an exception handler
# around it
#
# To run this server in uwsgi with 4 workers listening on port 9999 use:
# uwsgi -M -p 4 --http :9999 --wsgi-file _this_file_
# To run a using the single threaded python BaseHTTP service
# listening on port 9999 by default execute this file
#
try:
    import uwsgi
# Before we do anything with the application, see if the
# configs specify patching all std routines to be asynch
# *ONLY* use this if you are going to wrap the service in
# a wsgi container that has enabled gevent, such as
# uwsgi with the --gevent option
    if config is not None and config.get('gevent_monkeypatch_all', False):
        print("Monkeypatching std libraries for async")
        from gevent import monkey
        monkey.patch_all()
    uwsgi.applications = {'': application}
except ImportError:
    # Not available outside of wsgi, ignore
    pass

_proc = None


def start_server(host='localhost', port=0, newprocess=False):
    '''
    By default, will start the server on localhost on a system assigned port
    in the main thread. Execution of the main thread will stay in the server
    main loop until interrupted. To run the server in a separate process, and
    thus allow the stop_server method to be called, set newprocess = True. This
    will also allow returning of the port number.'''

    global _proc
    if _proc:
        raise RuntimeError('server is already running')
    httpd = make_server(host, port, application)
    port = httpd.server_address[1]
    print("Listening on port %s" % port)
    if newprocess:
        _proc = Process(target=httpd.serve_forever)
        _proc.daemon = True
        _proc.start()
    else:
        httpd.serve_forever()
    return port


def stop_server():
    global _proc
    _proc.terminate()
    _proc = None


if __name__ == "__main__":
    try:
        opts, args = getopt(sys.argv[1:], "", ["port=", "host="])
    except GetoptError as err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        sys.exit(2)
    port = 9999
    host = 'localhost'
    for o, a in opts:
        if o == '--port':
            port = int(a)
        elif o == '--host':
            host = a
            print("Host set to %s" % host)
        else:
            assert False, "unhandled option"

    start_server(host=host, port=port)
