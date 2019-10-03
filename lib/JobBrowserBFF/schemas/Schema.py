from jsonschema import validate
from jsonschema.exceptions import ValidationError
import os
import json

DEFAULT_SCHEMA_DIR = 'json'

class SchemaError(Exception):
    def __init__(self, message, path, value):
        self.message = message
        self.path = path
        self.value = value

class Schema(object):
    def __init__(self, schema_dir=None, load_schemas=False):
        if schema_dir is not None or load_schemas:
            self.schemas = self.load(schema_dir)
        else:
            self.schemas = {}

    def load(self, schema_dir=None):
        if schema_dir is None:
            schema_dir = os.path.dirname(__file__) + '/' +  DEFAULT_SCHEMA_DIR
        schemas = {}
        for file_name in os.listdir(schema_dir):
            file_path = os.path.join(schema_dir, file_name)
            file_base_name = os.path.splitext(file_name)[0]

            with open(file_path) as f:
                schema = json.load(f)
                schemas[file_base_name] = schema
        return schemas

    def validate(self, schema_key, data):
        schema = self.schemas.get(schema_key, None)
        if schema is None:
            raise ValueError('Schema "' + schema_key + '" does not exist')
        try:
            validate(instance=data, schema=schema)
        except ValidationError as ex:
            message = ex.message
            path = '.'.join(ex.absolute_schema_path)
            value = ex.validator_value
            raise SchemaError(message, path, value)

    def get(self, schema_name, default_value=None):
        return self.schemas.get(schema_name, default_value)