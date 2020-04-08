from biokbase.DynamicServiceClient import DynamicServiceClient
from biokbase.GenericClient import GenericClient
from biokbase.Errors import ServiceError
from JobBrowserBFF.model.KBaseServices import KBaseServices
import requests
import re


def get_value(d, keys, default_value=None):
    for key in keys:
        if key in d:
            d = d[key]
        else:
            return default_value
    return d


def raw_job_to_app(raw_job):
    app_id = raw_job.get('app_id')
    app_tag = raw_job.get('app_tag')
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
                        'function_name': function_name,
                        'tag': app_tag
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
                'function_name': function_name,
                'tag': app_tag
            }
    else:
        app = None
    return app


def raw_job_to_state(raw_job, client_group):
    raw_state = raw_job['state']
    if raw_state == 'queue':
        return {
            'status': 'queue',
            'create_at': raw_job['creation_time'],
            'queue_at': raw_job['creation_time'],
            'client_group': client_group
        }
    elif raw_state == 'run':
        return {
            'status': 'run',
            'create_at': raw_job['creation_time'],
            'queue_at': raw_job['creation_time'],
            'run_at': raw_job['exec_start_time'],
            'client_group': client_group
        }
    elif raw_state == 'complete':
        return {
            'status': 'complete',
            'create_at': raw_job['creation_time'],
            'queue_at': raw_job['creation_time'],
            'run_at': raw_job['exec_start_time'],
            'finish_at': raw_job['finish_time'],
            'client_group': client_group
        }
    elif raw_state == 'error':
        state = {
            'status': 'error',
            'create_at': raw_job['creation_time'],
            'queue_at': raw_job['creation_time'],
            'finish_at': raw_job['finish_time'],
            'error': {
                'code': 1,
                'message': raw_job.get('status', '')
                # TODO: add jsonrpc_error, which can hold either
                # a jsonrpc 1.1 (kbase) or 2.0 error.
            },
            'client_group': client_group
        }
        if 'exec_start_time' in raw_job:
            state['run_at'] = raw_job['exec_start_time']
        return state
    elif raw_state == 'cancel':
        state = {
            'status': 'terminate',
            'create_at': raw_job['creation_time'],
            'queue_at': raw_job['creation_time'],
            'finish_at': raw_job['finish_time'],
            'reason': {
                'code': 0
            },
            'client_group': client_group
        }
        # reason omitted because not supported by kb_Metrics
        if 'exec_start_time' in raw_job and raw_job['exec_start_time'] is not None:
            state['run_at'] = raw_job['exec_start_time']

        return state
    else:
        raise ValueError('Unrecognized state: ' + raw_state)


def raw_job_to_context(raw_job, workspaces_map):
    workspace_id = raw_job.get('wsid', None)
    if workspace_id is None:
        # print('NO WORKSPACE', raw_job)
        if raw_job.get('app') and 'export' in raw_job['app']['function_name']:
            # elif app is not None and 'export' in app['function_name']:
            job_type = 'export'
        else:
            job_type = 'unknown'
    else:
        workspace_id = int(workspace_id)
        workspace = workspaces_map.get(workspace_id, None)

        if workspace['is_accessible']:
            if workspace.get('narrative'):
                job_type = 'narrative'
            elif raw_job.get('app') and 'export' in raw_job['app'].get('function_name', ''):
                # elif app is not None and 'export' in app['function_name']:
                job_type = 'export'
            else:
                job_type = 'workspace'
        else:
            job_type = 'workspace'

    if job_type == 'narrative':
        context = {
            'type': 'narrative',
            'workspace': {
                'id': int(workspace_id),
                'is_accessible': True,
                'name': workspace.get('name', None),
                'is_deleted': workspace.get('is_deleted', None)
            },
            'narrative': {
                'title': workspace['narrative'].get('title', None)
            }
        }
    elif job_type == 'export':
        context = {
            'type': 'export'
        }
    elif job_type == 'workspace':
        ws = {
            'id': int(workspace_id),
            'is_accessible': workspace['is_accessible'],
        }

        if workspace['is_accessible']:
            ws['name'] = workspace['name']

        context = {
            'type': 'workspace',
            'workspace': ws
        }
    else:
        context = {
            'type': 'unknown'
        }
    return context


def raw_job_to_job(raw_job, apps_map, users_map, workspaces_map):
    # Get the additional user info out of the users map
    user_info = users_map.get(raw_job['user'], None)
    if user_info is not None:
        realname = user_info['realname']
    else:
        realname = raw_job['user']

    # Get the additional app info out of the apps map
    app = raw_job.get('app', None)
    client_group = None
    if app is not None:
        app_info = apps_map.get(app['id'], None)

        if app_info is None:
            app['title'] = app['id']
            app['client_groups'] = []
        else:
            app['title'] = app_info['name']
            app['client_groups'] = app_info['client_groups']
            if len(app['client_groups']) > 0:
                client_group = app['client_groups'][0]

    # Get the additional workspace info out of the workspaces map, and
    # also handle multiple types of workspace
    context = raw_job_to_context(raw_job, workspaces_map)

    job = {
        'job_id': raw_job['job_id'],
        'state': raw_job_to_state(raw_job, client_group),
        'app': app,
        'owner': {
            'username': raw_job['user'],
            'realname': realname
        },
        'context': context
    }

    return job


def raw_log_line_to_entry(raw_log_line, entry_number, offset):
    if raw_log_line.get('is_error', False):
        level = 'error'
    else:
        level = 'normal'
    return {
        'logged_at': entry_number + offset,
        'message': raw_log_line['line'],
        'level': level,
        'row': entry_number + offset
    }


class KBMetricsModel(object):
    NOT_FOUND_RE = re.compile('^There is no job .+ viewable by user .+$')

    def __init__(self, config, token, username, modules, timeout):
        self.config = config
        self.token = token
        self.username = username
        self.timeout = timeout
        self.modules = modules

    def get_service_ver(self, module_name):
        module = self.modules['kb_Metrics']
        if module is not None:
            return module.get('tag', None)
        else:
            return None

    def get_job(self, job_id):
        url = self.config['srv-wiz-url']
        service_ver = self.get_service_ver('kb_Metrics')
        rpc = DynamicServiceClient(url=url,
                                   module='kb_Metrics',
                                   token=self.token,
                                   service_ver=service_ver)
        try:
            params = {
                'job_id': job_id
            }
            result = rpc.call_func('get_job', params)

            # Validate result
            if 'job_state' not in result:
                raise ServiceError(code=40000, message='Unexpected response')

            job_state = result['job_state']
            # A job state with a value of None means that the job was not found
            if job_state is None:
                raise ServiceError(code=40100, message='Job not found')

            return job_state
        except ServiceError:
            raise
        except Exception as err:
            raise ServiceError(code=40000, message='Unknown error', data={
                'original_message': str(err)
            })

    def is_admin(self):
        url = self.config['srv-wiz-url']
        service_ver = self.get_service_ver('kb_Metrics')
        rpc = DynamicServiceClient(url=url,
                                   module='kb_Metrics',
                                   token=self.token,
                                   service_ver=service_ver,
                                   # TODO: default timeout needs to be in config.
                                   timeout=self.timeout)
        try:
            result = rpc.call_func('is_admin', {})
            return result['is_admin']
        except ServiceError:
            raise
        except Exception as ex:
            raise ServiceError(code=40000, message='Unknown error', data={
                'original_message': str(ex)
            })

    def metrics_query_jobs(self, filter=None, search=None, offset=None,
                           limit=None, time_span=None, timeout=None, sort=None, is_admin=False):
        service_ver = self.get_service_ver('kb_Metrics')
        rpc = DynamicServiceClient(url=self.config['srv-wiz-url'],
                                   module='kb_Metrics',
                                   token=self.token,
                                   timeout=timeout,
                                   service_ver=service_ver)

        try:
            params = {
                'offset': offset,
                'limit': limit,
                'timeout': timeout
            }

            if filter is not None:
                params['filter'] = filter

            if time_span:
                params['epoch_range'] = [time_span['from'], time_span['to']]

            if sort:
                params['sort'] = list(
                    map(lambda x: {'field': x['key'], 'direction': x['direction']}, sort))

            if search:
                params['search'] = list(
                    map(lambda x: {'term': x, 'type': 'regex'}, search['terms']))

            if is_admin:
                method = 'query_jobs_admin'
            else:
                method = 'query_jobs'
            jobs = rpc.call_func(method, params)

            return jobs['job_states'], jobs['found_count'], jobs['total_count']
        except ServiceError as se:
            print('SERVICE ERROR', se.message)
            raise
        except Exception as ex:
            raise ServiceError(code=40000, message='Unknown error', data={
                'original_message': str(ex)
            })

    def query_jobs(self, params):
        is_admin = params.get('admin', False)
        if is_admin:
            if not self.is_admin():
                raise ServiceError(
                    code=50,
                    message='Permission denied for this operation',
                    data={})

        raw_jobs, found_count, total_count = self.metrics_query_jobs(
            offset=params.get('offset', None),
            limit=params.get('limit', None),
            filter=params.get('filter', None),
            time_span=params.get('time_span', None),
            timeout=params.get('timeout', self.timeout),
            sort=params.get('sort', None),
            search=params.get('search', None),
            is_admin=is_admin
        )

        # Where possible we do a batch request.
        usernames = set()
        apps_to_fetch = dict()
        workspace_ids = set()

        for raw_job in raw_jobs:
            usernames.add(raw_job['user'])

            if 'app_id' in raw_job:
                app = raw_job_to_app(raw_job)
                raw_job['app'] = app
                if app is not None:
                    apps_to_fetch[app['id']] = app
            else:
                # TODO: does this ever really happen?
                raw_job['app'] = None

            if 'wsid' in raw_job:
                workspace_ids.add(int(raw_job['wsid']))

        services = KBaseServices(config=self.config, token=self.token)

        # Get a dict of unique users for this set of jobs
        users_map = services.get_users(list(usernames))

        # Get a dict of unique users for this set of jobs.
        apps_map = dict()
        apps = services.get_apps(list(apps_to_fetch.values()))
        for app_id, app in apps.items():
            if app is not None:
                apps_map[app_id] = app

        workspaces_map = dict()
        workspaces = services.get_workspaces(list(workspace_ids))
        for workspace in workspaces:
            workspaces_map[workspace['id']] = workspace

        # Now join them all together.
        jobs = []
        for raw_job in raw_jobs:
            job = raw_job_to_job(raw_job, apps_map, users_map, workspaces_map)
            jobs.append(job)

        # Now DONE!
        return jobs, found_count, total_count

    def match_field(self, expr, obj, path):
        value = get_value(obj, path)
        if value is None:
            return False
        return re.search(expr, value)

    def get_users(self, user_ids):
        url = self.config['auth-url']

        header = {
            'Accept': 'application/json',
            'Authorization': self.token,
        }

        endpoint = url + '/api/V2/users/?list=' + ','.join(user_ids)

        response = requests.get(endpoint, headers=header, timeout=self.timeout/1000)
        if response.status_code != 200:
            raise ServiceError(code=40000, message='Error fetching users',
                               data={'user_id': user_ids})
        else:
            try:
                result = response.json()
                retval = dict()
                for username, realname in result.items():
                    retval[username] = {
                        'realname': realname
                    }
                return retval
            except Exception as err:
                raise ServiceError(code=40000, message='Bad response', data={
                                   'user_id': user_ids, 'original_message': str(err)})

    def get_client_groups(self):
        url = self.config['catalog-url']
        rpc = GenericClient(url=url, module="Catalog", token=self.token)
        # Note that an empty params is sent - this is due to the definition of this
        # catalog method -- it is specified with an empty struct as the param!
        result = rpc.call_func('get_client_groups', {})
        return result

    def get_job_log(self, job_id, offset=None, limit=None, search=None, level=None):
        url = self.config['njsw-url']

        rpc = GenericClient(url=url, module="NarrativeJobService",
                            token=self.token, timeout=self.timeout)

        try:
            result = rpc.call_func('get_job_logs', {
                'job_id': job_id,
                'skip_lines': offset
            })
        except ServiceError as se:
            if re.search('There is no job .+ viewable by user .+', se.message):
                raise ServiceError(
                    code=40,
                    message='Permission denied for this job',
                    data={})
            else:
                raise
        except Exception:
            # TODO: better munging of some other exception into service error.
            # Maybe put this in biokbase.Errors.
            raise ServiceError(
                code=1,
                message='Unknown error',
                data={}
            )

        lines = result['lines'][0:limit]
        entries = [raw_log_line_to_entry(line, index, offset) for index, line in enumerate(lines)]

        return {
            'log': entries,
            'total_count': len(result['lines'])
        }

    def cancel_job(self, params):
        url = self.config['njsw-url']

        rpc = GenericClient(
            url=url,
            module="NarrativeJobService",
            token=self.token,
            timeout=self.timeout)

        try:
            rpc.call_func('cancel_job', {
                'job_id': params['job_id']
            })
            return None
        except ServiceError as se:
            if self.NOT_FOUND_RE.match(se.message):
                raise ServiceError(
                    code=10,
                    message='Job not found',
                    data={
                        'job_id': params['job_id']
                    })
            else:
                raise ServiceError(
                    code=1,
                    message='Unknown error',
                    data={
                        'upstream-error': {
                            'code': se.code,
                            'message': se.message,
                            'data': se.data
                        }
                    }
                )
        except Exception as ex:
            if hasattr(ex, 'message'):
                message = ex.message
            else:
                message = None
            raise ServiceError(
                code=1,
                message='Unknown error',
                data={
                    'message': message
                }
            )

    def get_jobs(self, params):
        filter = {
            'job_id': params['job_ids']
        }

        query_jobs_params = {
            'offset': 0,
            'limit': len(params['job_ids']),
            'timeout': params['timeout'],
            'filter': filter,
            'admin': params.get('admin', 0)}

        # TODO: hmm, need different implementation.
        jobs, found_count, total_count = self.query_jobs(query_jobs_params)

        if len(jobs) != len(params['job_ids']):
            # TODO: compute missing jobs for the data
            raise ServiceError(
                code=10,
                message='One or more jobs not found',
                # TODO: add missing jobs
                data={})
        else:
            return jobs
