from jsonrpcbase import InvalidParamsError
from JobBrowserBFF.schemas.Schema import Schema, SchemaError

class Validation(object):
    def __init__(self, load_schemas=False):
        self.schema = Schema(load_schemas=load_schemas)

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
    