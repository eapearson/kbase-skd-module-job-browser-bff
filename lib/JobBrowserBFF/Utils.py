import os
import toml
import json
from biokbase.Errors import ServiceError
from datetime import datetime

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
        raise ServiceError(code=40000, message="Error loading definition", data={'file': file_name})
 
def ms_to_iso(ms_time):
    return datetime.fromtimestamp(ms_time / 1000).isoformat(timespec="seconds") + 'Z'

def iso_to_ms(iso):
    return round(datetime.fromisoformat(iso).timestamp() * 1000)
    
def parse_app_id(app_id):
    if app_id is not None:
        app_id_parts = app_id.split('/')
        if len(app_id_parts) != 2:
            # main category of oddly formed app ids simple doesn't have the
            # correct number of elements.
            if len(app_id_parts) == 3:
                if len(app_id_parts[2]) == 0:
                    # Some have a / at the end
                    module_name, function_name, xtra = app_id_parts
                    id = '/'.join([module_name, function_name])
                    app = {
                        'id': id,
                        'module_name': module_name,
                        'function_name': function_name
                    }
                else:
                    app = None
            else:
                app = None
        else:
            # normal case
            module_name, function_name = app_id_parts
            app = {
                'id': app_id,
                'module_name': module_name,
                'function_name': function_name
            }
    else:
        app = None
    return app
