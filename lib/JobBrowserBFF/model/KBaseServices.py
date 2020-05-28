import requests
from biokbase.GenericClient import GenericClient
from biokbase.Errors import ServiceError
from cachetools import cached, TTLCache
# from cachetools.keys import hashkey
# from functools import partial


class KBaseServices(object):
    def __init__(self, config=None, token=None, username=None,  timeout=10000):
        self.token = token

        self.config = config
        self.timeout = timeout
        self._cached_users = TTLCache(maxsize=10000, ttl=600)
        # self._cached_workspaces = dict()
        self.username = self.get_user()['username']

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
        url = self.config['auth-url']

        header = {
            'Accept': 'application/json',
            'Authorization': self.token,
        }

        result = dict()
        users_to_get = []

        for user_id in user_ids:
            if user_id in self._cached_users:
                result[user_id] = self._cached_users[user_id]
            else:
                users_to_get.append(user_id)

        endpoint = url + '/api/V2/users/?list=' + ','.join(users_to_get)

        response = requests.get(endpoint, headers=header, timeout=10)
        if response.status_code != 200:
            raise ServiceError(code=40000, message='Error fetching users',
                               data={'user_id': user_ids})
        else:
            try:
                result = response.json()
                for username, realname in result.items():
                    user = {
                        'realname': realname
                    }
                    result[username] = user
                    self._cached_users[username] = user
            except Exception as err:
                raise ServiceError(code=40000, message='Bad response', data={
                                   'user_id': user_ids, 'original_message': str(err)})
            return result

    # Fetch the entire app catalog.
    # Cached for up to 10 minutes
    @cached(cache=TTLCache(maxsize=10000, ttl=600))
    def get_app_catalog(self):
        url = self.config['nms-url']
        rpc = GenericClient(url=url, module="NarrativeMethodStore",
                            token=self.token, timeout=self.timeout)
        apps = dict()
        for tag in ['dev', 'beta', 'release']:
            apps[tag] = dict()
            methods = rpc.call_func('list_methods', {
                'tag': tag
            })
            for method in methods:
                apps[tag][method['id']] = method
        return apps

    def get_apps(self, apps_to_fetch):
        catalog = self.get_app_catalog()

        client_groups = self.get_client_groups()

        app_client_groups_map = dict()
        for client_group in client_groups:
            app_id = client_group['app_id']
            app_client_groups_map[app_id] = client_group['client_groups']

        apps = dict()
        for app_to_fetch in apps_to_fetch:
            app_id = app_to_fetch['id']
            tag = app_to_fetch.get('tag')
            if (tag is None):
                app = (catalog.get('release').get(app_id) or
                       catalog.get('beta').get(app_id) or
                       catalog.get('dev').get(app_id) or
                       None)
            else:
                app = catalog.get(tag).get(app_id)

            if app is None:
                # TODO: use a global logger hooked into the kbase logger which is
                # currently setup and owned by the server.
                # It seems too much to thread the logger through all the method calls
                # to get here.
                print('WARNING: app not found', app_id)
                continue
            apps[app_id] = {
                'info': app,
                'client_groups': app_client_groups_map.get(app_id, ['njs'])
            }
            # apps[app_id]['client_groups'] = app_client_groups_map.get(app_id, ['njs'])

        return apps
    # @cached(cache=TTLCache(maxsize=10000, ttl=600, key=partial(hashkey, self.token)))

    # @cached(cache=TTLCache(maxsize=10000, ttl=600))
    def get_all_workspaces(self, username):
        url = self.config['workspace-url']
        rpc = GenericClient(url=url, module="Workspace", token=self.token, timeout=self.timeout)

        return rpc.call_func('list_workspace_info', {
            'showDeleted': 0
        })

    def get_workspaces(self, workspace_ids):
        # TODO: should be username
        workspaces = self.get_all_workspaces(self.username)

        workspaces_map = dict()
        for info in workspaces:
            workspaces_map[info[0]] = info

        result = []

        for workspace_id in workspace_ids:
            workspace_info = workspaces_map.get(workspace_id, None)
            if workspace_info is None:
                result.append({
                    'id': workspace_id,
                    'is_accessible': False
                })
                continue

            [id, name, owner, moddate, max_objid, user_permission,
                globalread, lockstat, metadata] = workspace_info

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

            result.append(info)

        return result

    @cached(cache=TTLCache(maxsize=10000, ttl=600))
    def get_client_groups(self):
        url = self.config['catalog-url']
        rpc = GenericClient(url=url, module="Catalog", token=self.token, timeout=self.timeout)
        # Note that an empty params is sent - this is due to the definition of this
        # catalog method -- it is specified with an empty struct as the param!
        result = rpc.call_func('get_client_groups', {})
        return result
