# -*- coding: utf-8 -*-

import time
from biokbase.GenericClient import GenericClient

# Default timeout for upstream calls is 10 minutes; propagated to
# the generic client.
DEFAULT_TIMEOUT = 600

# Default lifetime for cached urls is 5 minutes.
DEFAULT_CACHE_LIFETIME = 300


class URLCache:
    _url_cache = dict()

    def __init__(self, ttl=DEFAULT_CACHE_LIFETIME):
        self.ttl = ttl

    def set_url(self, name, url, ttl=None):
        if ttl is None:
            ttl = self.ttl

        self._url_cache.set(name, {
            'created': time.time(),
            'ttl': ttl,
            'url': url
        })

    def get_url(self, name):
        cache_entry = self._url_cache.get(name)
        if cache_entry is None:
            return None
        elapsed = time.time() - cache_entry['created']
        if elapsed > cache_entry['ttl']:
            del self._url_cache[name]
            return None
        return cache_entry['url']


global_url_cache = URLCache()


class DynamicServiceClient:
    def __init__(self, url=None, module=None, token=None,
                 service_ver=None,
                 cache_lifetime=DEFAULT_CACHE_LIFETIME,
                 timeout=None):
        self.service_wizard_url = url
        self.service_ver = service_ver
        self.module_name = module
        self.cache_lifetime = cache_lifetime
        self.cached_url = None
        self.last_fetched_at = None
        self.token = token
        self.timeout = timeout

    def call_func(self, method, params=None, timeout=None):
        timeout = timeout or self.timeout

        # If not cached or cache entry is expired, re-fetch the url from
        # the service wizard.
        service_url = self._get_url(timeout)

        client = GenericClient(module=self.module_name,
                               url=service_url,
                               token=self.token,
                               timeout=timeout)

        return client.call_func(method, params)

    def _get_url(self, timeout):
        url = global_url_cache.get_url(self.module_name)
        if url is not None:
            return url
        url = self._lookup_url(timeout)
        global_url_cache.set_url(self.module_name, url)
        return url

    def _lookup_url(self, timeout):
        service_wizard = GenericClient(module='ServiceWizard',
                                       url=self.service_wizard_url,
                                       token=self.token,
                                       timeout=timeout)

        params = {
            'module_name': self.module_name,
            'version': self.service_ver
        }
        result = service_wizard.call_func('get_service_status', params)
        return result['url']
