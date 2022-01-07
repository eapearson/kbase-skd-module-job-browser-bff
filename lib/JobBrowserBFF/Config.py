from os import environ
from JobBrowserBFF.constants import DEPLOY, SERVICE
from configparser import ConfigParser


class Config:
    def __init__(self):
        self.__config = None
        self.__has_config = None

    def get_config_file(self):
        return environ.get(DEPLOY, None)

    def get_service_name(self):
        return environ.get(SERVICE, None)

    def get_config(self):
        if self.__has_config:
            return self.__config
        elif self.__has_config is False:
            return None
        else:
            if not self.get_config_file():
                self.__has_config is False
                return None
            self.__config = dict()
            config = ConfigParser()
            config.read(self.get_config_file())
            for nameval in config.items(self.get_service_name() or "JobBrowserBFF"):
                self.__config[nameval[0]] = nameval[1]
            return self.__config

    def get(self, key, default_value=None):
        config = self.get_config()
        if config is None:
            return default_value
        return config.get(key, default_value)

    def get_int(self, key, default_value=None):
        value = self.get(key, default_value=None)
        if value is not None:
            return int(value)

    def test(self, key, test_value, default_value=None):
        config = self.get_config()
        if config is None:
            return default_value
        if key not in config:
            return default_value
        value = config[key]
        return value == test_value
