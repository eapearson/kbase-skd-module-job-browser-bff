import os
import json

DEFAULT_DATA_DIR = "json"


class DefinitionError(Exception):
    pass


class Definitions(object):
    def __init__(self, data_dir=None, load=False):
        if data_dir is not None or load:
            self.definitions = self.load(data_dir)
        else:
            self.definitions = {}

    def load(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.dirname(__file__) + "/" + DEFAULT_DATA_DIR
        definitions = {}
        for file_name in os.listdir(data_dir):
            file_path = os.path.join(data_dir, file_name)
            file_base_name = os.path.splitext(file_name)[0]

            with open(file_path) as f:
                definition = json.load(f)
                definitions[file_base_name] = definition
        return definitions

    def get(self, definition_name, default_value=None):
        return self.definitions.get(definition_name, default_value)
