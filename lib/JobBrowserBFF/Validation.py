from jsonrpcbase import InvalidParamsError
from JobBrowserBFF.schemas.Schema import Schema, SchemaError


class Validation(object):
    def __init__(self, schema_dir=None, load_schemas=None):
        self.schema = Schema(schema_dir=schema_dir, load_schemas=load_schemas)

    def validate_params(self, method_name, data):
        schema_key = method_name + '_params'
        try:
            self.schema.validate(schema_key, data)
        except SchemaError as ex:
            raise InvalidParamsError(data={
                'schema_error': ex.message,
                'schema_path': ex.path,
                'schema_value': ex.value
            })

    def validate_result(self, method_name, data):
        schema_key = method_name + '_result'
        try:
            self.schema.validate(schema_key, data)
        except SchemaError as ex:
            raise InvalidParamsError(data={
                'schema_error': ex.message,
                'schema_path': ex.path,
                'schema_value': ex.value
            })

    def validate(self, schema_key, data):
        try:
            self.schema.validate(schema_key, data)
        except SchemaError as ex:
            raise ex

    def validate_config(self, data):
        schema_key = 'config'
        try:
            self.schema.validate(schema_key, data)
        except SchemaError as ex:
            raise InvalidParamsError(data={
                'schema_error':  ex.message,
                'schema_path': ex.path,
                'schema_value': ex.value
            })
