# -*- coding: utf-8 -*-
import os
import time
import unittest
import json
from configparser import ConfigParser
import traceback
import io
from JobBrowserBFF.JobBrowserBFFImpl import JobBrowserBFF
from JobBrowserBFF.JobBrowserBFFServer import MethodContext
from JobBrowserBFF.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace


class TestBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('JobBrowserBFF'):
            cls.cfg[nameval[0]] = nameval[1]

        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)

        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'JobBrowserBFF',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
       
        cls.serviceImpl = JobBrowserBFF(cls.cfg)
        cls.scratch = cls.cfg['scratch']

        # Use the test configuration, because there are test values in there which are
        # not integrated into deploy.cfg since they are only for tests.
        test_cfg_file = '/kb/module/work/test.cfg'
        test_cfg_text = "[test]\n"
        with open(test_cfg_file, "r") as f:
            test_cfg_text += f.read()
        config = ConfigParser()
        config.readfp(io.StringIO(test_cfg_text))
        cls.test_config = dict(config.items("test"))
    
    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    @classmethod
    def tearDownClass(cls):
        pass

    



