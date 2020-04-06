# -*- coding: utf-8 -*-
import os
import time
import unittest
import json
from configparser import ConfigParser
import traceback
import io
from JobBrowserBFF.JobBrowserBFFImpl import JobBrowserBFF
from JobBrowserBFF.JobBrowserBFF_JSONRPCServer import MethodContext
from JobBrowserBFF.authclient import KBaseAuth as _KBaseAuth
from biokbase.Errors import ServiceError

from installed_clients.WorkspaceClient import Workspace


class TestBase(unittest.TestCase):

    @classmethod
    def loadConfig(cls):
        # The standard deployment configuration
        cls.cfg = {}
        config = ConfigParser()
        config.read(cls.config_file)
        for nameval in config.items('JobBrowserBFF'):
            cls.cfg[nameval[0]] = nameval[1]

        # Use the test configuration, because there are test values in there which are
        # not integrated into deploy.cfg since they are only for tests.

        # NB: standard location for test config.
        # TODO: should this be configurable itself? E.g. from env variable?
        test_cfg_file = '/kb/module/work/test.cfg'
        test_cfg_text = "[test]\n"
        with open(test_cfg_file, "r") as f:
            test_cfg_text += f.read()
        test_config = ConfigParser()
        test_config.readfp(io.StringIO(test_cfg_text))
        cls.test_config = dict(test_config.items("test"))

    @classmethod
    def loadEnvironment(cls):
        cls.token = os.environ.get('KB_AUTH_TOKEN', None)
        cls.config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)

    @classmethod
    def loadContext(cls):
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': cls.token,
                        'user_id': cls.user_id,
                        'provenance': [
                            {'service': 'JobBrowserBFF',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})

    @classmethod
    def loadAuth(cls):
        # Getting username from Auth profile for token
        if cls.token:
            authServiceUrl = cls.cfg['auth-service-url']
            auth_client = _KBaseAuth(authServiceUrl)
            cls.user_id = auth_client.get_user(cls.token)
        else:
            cls.user_id = None

    @classmethod
    def setUpClass(cls):
        cls.loadEnvironment()
        cls.loadConfig()
        cls.loadAuth()
        cls.loadContext()

        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.serviceImpl = JobBrowserBFF(cls.cfg)
        cls.scratch = cls.cfg['scratch']

    def getImpl(self):
        return self.__class__.serviceImpl

    def get_config(self, key, default_value=None):
        return self.cfg.get(key, default_value)

    def newAuth(self, token):
        # Getting username from Auth profile for token
        if token:
            authServiceUrl = self.cfg['auth-service-url']
            auth_client = _KBaseAuth(authServiceUrl)
            user_id = auth_client.get_user(token)
        else:
            user_id = None
        return user_id

    def new_context(self, token):
        ctx = MethodContext(None)
        user_id = self.newAuth(token)
        ctx.update({
            'token': token,
            'user_id': user_id,
            'provenance': [
                {'service': 'JobBrowserBFF',
                    'method': 'please_never_use_it_in_production',
                    'method_params': []
                 }],
            'authenticated': 1})
        return ctx

    def new_implementation_instance(self):
        return JobBrowserBFF(self.cfg)

    def getContext(self):
        return self.__class__.ctx

    def set_config(self, key, value):
        self.__class__.cfg[key] = value
        self.__class__.serviceImpl = JobBrowserBFF(self.__class__.cfg)

    @classmethod
    def tearDownClass(cls):
        pass

    @staticmethod
    def get_nested(some_dict, keys, default_value=None):
        for key in keys:
            if key in some_dict:
                some_dict = some_dict[key]
            else:
                return default_value
        return some_dict

    @staticmethod
    def is_in_descending_order(items, keys):
        in_order = True
        value_last = None
        for item in items:
            value = TestBase.get_nested(item, keys)
            if value_last is None:
                value_last = value
            else:
                if value <= value_last:
                    value_last = value
                else:
                    in_order = False
                    break
        return in_order

    @staticmethod
    def is_in_ascending_order(items, keys):
        in_order = True
        value_last = None
        for item in items:
            value = TestBase.get_nested(item, keys)
            if value_last is None:
                value_last = value
            else:
                if value >= value_last:
                    value_last = value
                else:
                    in_order = False
                    break
        return in_order

    def assert_in_ascending_order(self, items, keys):
        result = self.is_in_ascending_order(items, keys)
        self.assertTrue(result, 'Expected to be in ascending order, is not')

    def assert_in_descending_order(self, items, keys):
        result = self.is_in_descending_order(items, keys)
        self.assertTrue(result, 'Expected to be in descending order, is not')

    def assert_job_result_with_count(self, return_value):
        self.assertIsInstance(return_value, list)
        self.assertGreaterEqual(len(return_value), 1)
        result = return_value[0]
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result, dict)
        self.assertIn('jobs', result)
        jobs = result['jobs']
        self.assertIsInstance(jobs, list)
        self.assertIn('total_count', result)
        total_count = result['total_count']
        return jobs, total_count

    def assert_job_query_result_with_count(self, return_value):
        self.assertIsInstance(return_value, list)
        self.assertGreaterEqual(len(return_value), 1)
        result = return_value[0]
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result, dict)
        self.assertIn('jobs', result)
        jobs = result['jobs']
        self.assertIsInstance(jobs, list)
        self.assertIn('found_count', result)
        found_count = result['found_count']
        self.assertIn('total_count', result)
        total_count = result['total_count']
        return jobs, found_count, total_count

    def assert_job_result(self, return_value):
        self.assertIsInstance(return_value, list)
        self.assertGreaterEqual(len(return_value), 1)
        result = return_value[0]
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result, dict)
        self.assertIn('jobs', result)
        jobs = result['jobs']
        self.assertIsInstance(jobs, list)
        return jobs

    def error_message(self, ex):
        if hasattr(ex, 'message'):
            return ex.message
        else:
            return str(type(ex))

    def assert_no_exception(self, ex):
        try:
            print('Attempting to print the trace:')
            traceback.print_exc()
        except Exception as ex2:
            print('Error trying to print trace: ' + self.error_message(ex2))
            traceback.print_exc()
        if hasattr(ex, 'message'):
            error_type = type(ex)
            if error_type == ServiceError:
                print('DATA', ex.data)
                self.assertTrue(
                    False,
                    ('Did not expect an exception :'
                     ' ServiceError: {} - {} '.format(ex.code, ex.message)))
            else:
                self.assertTrue(False, 'Did not expect an exception {}:{} '.format(
                    ex.__class__.__name__, ex.message))
        else:
            self.assertTrue(False, 'Did not expect an exception (no message): {}'.format(type(ex)))

    # Just temporary, to bootstrap this thing.
    def new_mock_context(self, token):
        ctx = MethodContext(None)
        # user_id = self.newAuth(token)
        tokens = {
            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA': {
                'user_id': 'adminuser'
            },
            'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB': {
                'user_id': 'eaptest30'
            }
        }
        account = tokens[token]
        user_id = account['user_id']
        ctx.update({
            'token': token,
            'user_id': user_id,
            'provenance': [
                {'service': 'JobBrowserBFF',
                 'method': 'please_never_use_it_in_production',
                 'method_params': []
                 }],
            'authenticated': 1})
        return ctx

    def token_for(self, env, user_type):
        token = self.test_config['test_token_{}_{}'.format(env, user_type)]
        return token

    def impl_for(self, env, user_type):
        token = self.test_config['test_token_{}_{}'.format(env, user_type)]
        if env == 'mock':
            context = self.new_mock_context(token)
        else:
            context = self.new_context(token)
        return self.new_implementation_instance(), context
