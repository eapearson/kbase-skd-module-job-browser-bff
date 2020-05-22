# -*- coding: utf-8 -*-
import os
import unittest
from configparser import ConfigParser
import io
from JobBrowserBFF.JobBrowserBFFImpl import JobBrowserBFF
from JobBrowserBFF.JobBrowserBFF_JSONRPCServer import MethodContext
from JobBrowserBFF.authclient import KBaseAuth as _KBaseAuth


class UnitTestBase(unittest.TestCase):

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

    def getContext(self):
        return self.__class__.ctx

    @classmethod
    def tearDownClass(cls):
        pass
