# -*- coding: utf-8 -*-

import time
from biokbase.GenericClient import GenericClient

class DynamicServiceClient:

    def __init__(self, url = None, module = None, token=None, service_ver = None, refresh_cycle_seconds = 300):
        self.sw_url = url
        self.service_ver = service_ver
        self.module_name = module
        self.refresh_cycle_seconds = refresh_cycle_seconds
        self.cached_url = None
        self.last_refresh_time = None
        self.token = token

    def call_func(self, method, params=None):
        # Validate arguments
        if not isinstance(method, str):
            raise ValueError('"method" must be a string')
        # if not isinstance(params, list):
        #     raise ValueError('"params" must be an array')
       
        # If not cached or cache entry is expired, re-fetch the url from
        # the service wizard.
        if (not self.cached_url) or (time.time() - self.last_refresh_time > 
                                     self.refresh_cycle_seconds):
            self.cached_url = self._lookup_url()
            self.last_refresh_time = time.time()

        client = GenericClient(module=self.module_name,
                               url=self.cached_url,
                               token=self.token)
                               
        return client.call_func(method, params)

    def _lookup_url(self):
        service_wizard = GenericClient(module='ServiceWizard',
                                       url=self.sw_url,
                                       token=self.token)
        param = {
            'module_name': self.module_name, 
            'version': self.service_ver
        }
        result = service_wizard.call_func('get_service_status', param)
        return result['url']