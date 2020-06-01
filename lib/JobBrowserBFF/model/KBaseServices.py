import requests
from biokbase.GenericClient import GenericClient
from biokbase.Errors import ServiceError
from JobBrowserBFF.cache.AppCache import AppCache
from JobBrowserBFF.cache.UserProfileCache import UserProfileCache


class KBaseServices(object):
    def __init__(self, config=None, token=None, username=None,  timeout=10000):
        self.token = token

        self.config = config
        self.timeout = timeout
        self.app_cache = AppCache(
            path=config['cache-directory'] + '/app.db',
            narrative_method_store_url=config['nms-url'],
            upstream_timeout=60
        )
        self.user_profile_cache = UserProfileCache(
            path=config['cache-directory'] + '/user_profile.db',
            user_profile_url=config['user-profile-url'],
            upstream_timeout=60
        )

    def get_user(self):
        url = self.config['auth-url']

        header = {
            'Accept': 'application/json',
            'Authorization': self.token,
        }

        endpoint = url + '/api/V2/me'

        response = requests.get(endpoint, headers=header, timeout=10)
        if response.status_code != 200:
            raise ServiceError(code=40000, message='Error fetching me')
        else:
            try:
                result = response.json()
                return {
                    'username': result['user'],
                    'realname': result['display']
                }

            except Exception as err:
                raise ServiceError(code=40000, message='Bad response', data={
                                   'original_message': str(err)})

    def get_users(self, user_ids):
        profiles = self.user_profile_cache.get(user_ids)
        profiles_map = dict()
        for [username, profile] in profiles:
            profiles_map[username] = {
                'username': username,
                'realname': profile['user']['realname']
            }
        return profiles_map

    def get_apps(self, apps_to_fetch):
        app_ids = [app['id'] for app in apps_to_fetch]
        fetched_apps = self.app_cache.get_items(app_ids)
        apps_db = {}
        for app_id, tag, app_info, lookup_app_id in fetched_apps:
            app_id_parts = lookup_app_id.split('/')
            if len(app_id_parts) == 2:
                module = app_id_parts[0]
                name = app_id_parts[1]
            else:
                module = None
                name = app_id_parts[0]

            app = {
                'id': lookup_app_id,
                'module_name': module,
                'function_name': name
            }

            if app_id is None:
                app['not_found'] = True
                app['title'] = app['name']
                app['type'] = 'unknown'
            else:
                app['not_found'] = False
                # the function name is not actually provided in the
                # app info. Weird.
                app['version'] = app_info['ver']
                if 'icon' in app_info:
                    app['icon_url'] = app_info['icon']['url']

                app['title'] = app_info['name']
                app['subtitle'] = app_info['subtitle']
                app['type'] = 'narrative'

            apps_db[app_id] = app

        return apps_db

    def get_workspaces(self, workspace_ids):
        url = self.config['workspace-url']
        rpc = GenericClient(url=url, module="Workspace", token=self.token, timeout=self.timeout)

        workspace_infos = []
        for workspace_id in workspace_ids:
            try:
                [id, name, owner, moddate, max_objid, user_permission,
                 globalread, lockstat, metadata] = rpc.call_func(
                     'get_workspace_info', {
                         'id': workspace_id
                     })

                if metadata.get('narrative', None) is None:
                    is_narrative = False
                else:
                    is_narrative = True

                info = {
                    'id': workspace_id,
                    'is_accessible': True,
                    'name': name,
                    'is_deleted': False
                }
                if (is_narrative):
                    if metadata.get('is_temporary', None) == 'true':
                        is_temporary = True
                    else:
                        is_temporary = False
                    info['narrative'] = {
                        'title': metadata.get('narrative_nice_name', None),
                        'is_temporary': is_temporary
                    }

                workspace_infos.append(info)
            except Exception:
                workspace_infos.append({
                    'id': workspace_id,
                    'is_accessible': False
                })

        return workspace_infos

    def get_client_groups(self):
        url = self.config['catalog-url']
        rpc = GenericClient(url=url, module="Catalog", token=self.token, timeout=self.timeout)
        # Note that an empty params is sent - this is due to the definition of this
        # catalog method -- it is specified with an empty struct as the param!
        result = rpc.call_func('get_client_groups', {})
        return result
