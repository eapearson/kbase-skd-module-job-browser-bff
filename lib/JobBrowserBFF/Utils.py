import os
import toml
import json
from biokbase.Errors import ServiceError

def load_definition(base_file_name, format='toml'):
    try:
        file_name = base_file_name + '.' + format
        f = os.path.dirname(os.path.realpath(__file__)) + '/definitions/' + file_name
        if format == 'toml':
            d = toml.load(f)
            return d['definitions']
        elif format == 'json':
            with open(f) as definitions_file:
                d = json.load(definitions_file)
                return d
        else:
            raise ServiceError(code=40000, message='Unrecognized definitions form "' + format + '"', data={'format': format})
    except Exception as e:
        # print(str(e))
        raise ServiceError(code=40000, message="Error loading definition", data={'file': file_name})
 