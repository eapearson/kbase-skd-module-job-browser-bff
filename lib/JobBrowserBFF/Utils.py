def parse_app_id(app_id, method):
    if app_id is not None and "/" in app_id:
        # This is the normal case - narrative methods
        app_id_parts = app_id.split("/")
        app_type = "narrative"
    elif method is not None:
        # Here we use the method for non-narrative methods.
        app_id_parts = method.split(".")
        app_type = "other"
    else:
        return None

    if len(app_id_parts) != 2:
        # Strange but true.
        if len(app_id_parts) == 3:
            if len(app_id_parts[2]) == 0:
                # Some have a / at the end
                module_name, function_name, xtra = app_id_parts
                id = "/".join([module_name, function_name])
                app = {
                    "id": id,
                    "module_name": module_name,
                    "function_name": function_name,
                    "type": app_type,
                }
            else:
                app = None
        else:
            app = None
    else:
        # normal case
        module_name, function_name = app_id_parts
        app = {
            "id": "/".join(app_id_parts),
            "module_name": module_name,
            "function_name": function_name,
            "type": app_type,
        }
    return app
