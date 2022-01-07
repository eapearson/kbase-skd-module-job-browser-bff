"""
Created on Aug 1, 2016

A very basic KBase auth client for the Python server.

@author: gaprice@lbl.gov
"""
import time
import requests
import threading
import hashlib


class TokenCache(object):
    """A basic cache for tokens."""

    _MAX_TIME_SEC = 5 * 60  # 5 min

    _lock = threading.RLock()

    def __init__(self, maxsize=2000):
        self._cache = {}
        self._maxsize = maxsize
        self._halfmax = maxsize / 2  # int division to round down

    def token_expired(self, cached_at):
        if time.time() - cached_at > self._MAX_TIME_SEC:
            return True
        return False

    def get_user(self, token):
        with self._lock:
            token_info = self._cache.get(token)
        if not token_info:
            return None

        username, cached_at = token_info
        if self.token_expired(cached_at):
            return None

        return username

    def encode_token(self, token):
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def add_valid_token(self, token, username):
        if not token:
            raise ValueError("Must supply token")
        if not username:
            raise ValueError("Must supply username")

        encoded_token = self.encode_token(token)
        with self._lock:
            self._cache[encoded_token] = [username, time.time()]
            if len(self._cache) > self._maxsize:
                sorted_items = sorted(
                    list(self._cache.items()), key=(lambda v: v[1][1])
                )
                for i, (t, _) in enumerate(sorted_items):
                    if i <= self._halfmax:
                        del self._cache[t]
                    else:
                        break


class KBaseAuth(object):
    """
    A very basic KBase auth client for the Python server.
    """

    def __init__(self, auth_url=None):
        """
        Constructor
        """
        if auth_url is None:
            raise ValueError("auth_url not provided to auth client")

        self._authurl = auth_url
        # TODO: is it really a good idea to have a default url? I think we
        #       should just fail if no url is provided; otherwise bad code,
        #       probably NOT in production, will call production.
        # if not self._authurl:
        #     self._authurl = self._LOGIN_URL
        self._cache = TokenCache()

    def get_user(self, token):
        if not token:
            raise ValueError("Must supply token")

        username = self._cache.get_user(token)
        if username:
            return username

        d = {"token": token, "fields": "user_id"}

        ret = requests.post(self._authurl, data=d)
        if not ret.ok:
            try:
                err = ret.json()
            except Exception:
                ret.raise_for_status()
            message = "Error connecting to auth service: {} {}\n{}\n{}".format(
                ret.status_code, ret.reason, err["error"]["message"], self._authurl
            )
            raise ValueError(message)

        username = ret.json()["user_id"]
        self._cache.add_valid_token(token, username)
        return username
