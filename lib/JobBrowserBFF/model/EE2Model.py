from biokbase.Errors import ServiceError
from JobBrowserBFF.model.EE2Api import EE2Api
from JobBrowserBFF.model.KBaseServices import KBaseServices
from JobBrowserBFF.Utils import parse_app_id
import re
import time


def get_param(params, key):
    if key not in params:
        raise ValueError(f'required param {key} not provided')
    return params.get(key)

# def get_path(the_dict, key_path, default_value=None):
#     if len(key_path) == 0:
#         return default_value
#     value = the_dict
#     for key in key_path:

#         if key == '*':
#             # this means the current value should be an array
#             # and the next

#         value = value.get(key)
#         if value is None:
#             return default_value
#         if not isinstance(value, dict):
#             return default_value
#     return value


def raw_job_to_state(raw_job):
    raw_state = raw_job['status']

    # which queue it is/was running on.
    client_group = find_in(['job_input', 'requirements', 'clientgroup'], raw_job, 'njs')

    if raw_state == 'created':
        return {
            'status': 'create',
            'create_at': raw_job['created']
        }
    if raw_state == 'queued':
        return {
            'status': 'queue',
            'create_at': raw_job['created'],
            'queue_at': raw_job['queued'],
            'client_group': client_group
        }
    elif raw_state == 'running':
        return {
            'status': 'run',
            'create_at': raw_job['created'],
            'queue_at': raw_job['queued'],
            'run_at': raw_job['running'],
            'client_group': client_group
        }
    elif raw_state == 'completed':
        return {
            'status': 'complete',
            'create_at': raw_job['created'],
            'queue_at': raw_job['queued'],
            'run_at': raw_job['running'],
            # TODO: finished is not being set in many cases!!
            # TODO: remove this workaround when that is fixed.
            'finish_at': raw_job.get('finished', raw_job.get('updated', None)),
            'client_group': client_group
        }
    elif raw_state == 'error':
        state = {
            'status': 'error',
            'create_at': raw_job['created'],
            'error': {
                'code': 1,
                'message': raw_job.get('errormsg', '')
            },
            'client_group': client_group
        }

        if 'queued' in raw_job:
            state['queue_at'] = raw_job['queued']

        if 'running' in raw_job:
            state['run_at'] = raw_job['running']

        if 'finished' in raw_job:
            state['finish_at'] = raw_job['finished']
        else:
            raise ValueError('"finished" timestamp required for "error" job')

        return state
    elif raw_state == 'terminated':
        state = {
            'status': 'terminate',
            'create_at': raw_job['created'],
            'reason': {
                'code': 0
            },
            'client_group': client_group
        }

        if 'queued' in raw_job:
            state['queue_at'] = raw_job['queued']

        if 'running' in raw_job:
            state['run_at'] = raw_job['running']

        if 'finished' in raw_job:
            state['finish_at'] = raw_job['finished']
        else:
            raise ValueError(
                '"finished" timestamp required for "terminated" job')

        return state
    else:
        raise ValueError('Unrecognized state: ' + raw_state)


def find_in(path, data, default_value=None):
    for el in path:
        if el in data:
            data = data[el]
        else:
            return default_value
    return data


def raw_job_to_job(raw_job, apps_map, users_map, workspaces_map):
    # Get the additional user info out of the users map
    user_info = users_map.get(raw_job['user'], None)
    if user_info is not None:
        realname = user_info['realname']
    else:
        realname = raw_job['user']

    # Get the additional app info out of the apps map
    app = raw_job.get('app', None)
    if app is not None:
        catalog_app = apps_map.get(app['id'], None)
        if catalog_app is None:
            app['not_found'] = True
            app['title'] = app['id']
            app['type'] = 'unknown'
        else:
            app = catalog_app
            # app['type'] = 'narrative'
            # app_info = catalog_app.get('info')
            # if app_info is None:
            #     app['not_found'] = True
            #     app['title'] = app['id']
            #     app['type'] = 'unknown'
            # else:
            # app['not_found'] = False
            # app['title'] = app_info['name']
            # app['subtitle'] = app_info.get('subtitle')
            # app['type'] = 'narrative'
            # app['icon_url'] = app_info.get('icon_url')
            # app['version'] = app_info.get('version')

    # Get the additional workspace info out of the workspaces map, and
    # also handle multiple types of workspace
    if 'job_input' in raw_job:
        job_input = raw_job['job_input']

        # Determine workspace type
        workspace_id = job_input.get('wsid', None)

        if workspace_id is None:
            workspace = None
            if app is not None and 'export' in app['function_name']:
                job_type = 'export'
            else:
                job_type = 'unknown'
        else:
            workspace = workspaces_map[workspace_id]
            if workspace['is_accessible']:
                if workspace.get('narrative'):
                    job_type = 'narrative'
                else:
                    job_type = 'workspace'
            else:
                job_type = 'workspace'

        if job_type == 'narrative':
            job = {
                'job_id': raw_job['job_id'],
                'state': raw_job_to_state(raw_job),
                'owner': {
                    'username': raw_job['user'],
                    'realname': realname
                },
                'context': {
                    'type': 'narrative',
                    'workspace': {
                        'id': int(workspace_id),
                        'is_accessible': True,
                        'name': workspace.get('name', None),
                        'is_deleted': workspace.get('is_deleted', None)
                    },
                    'narrative': {
                        'title': workspace['narrative'].get('title', None),
                        'is_temporary': workspace['narrative'].get('is_temporary')
                    }
                },
                'app': app
            }
        elif job_type == 'export':
            job = {
                'job_id': raw_job['job_id'],
                'state': raw_job_to_state(raw_job),
                'owner': {
                    'username': raw_job['user'],
                    'realname': realname
                },
                'app': app,
                'context': {
                    'type': 'export'
                }
            }
        elif job_type == 'workspace':
            ws = {
                'id': int(workspace_id),
                'is_accessible': workspace['is_accessible'],
            }

            if workspace['is_accessible']:
                ws['name'] = workspace['name']

            job = {
                'job_id': raw_job['job_id'],
                'state': raw_job_to_state(raw_job),
                'owner': {
                    'username': raw_job['user'],
                    'realname': realname
                },
                'app': app,
                'context': {
                    'type': 'workspace',
                    'workspace': ws
                }
            }
        else:
            job = {
                'job_id': raw_job['job_id'],
                'state': raw_job_to_state(raw_job),
                'owner': {
                    'username': raw_job['user'],
                    'realname': realname
                },
                'app': app,
                'context': {
                    'type': 'unknown'
                }
            }
    else:
        job = {
            'job_id': raw_job['job_id'],
            'state': raw_job_to_state(raw_job),
            'owner': {
                'username': raw_job['user'],
                'realname': realname
            },
            'app': app,
            'context': {
                'type': 'unknown'
            }
        }

    return job


def raw_log_line_to_entry(raw_log_line, entry_number, offset):
    if raw_log_line.get('is_error', False):
        level = 'error'
    else:
        level = 'normal'
    return {
        'logged_at': raw_log_line.get('ts'),
        'row': entry_number + offset,
        'message': raw_log_line['line'],
        'level': level
    }


class EE2Model(object):
    def __init__(self, config, token, timeout, username):
        self.config = config
        self.token = token
        # self.username = username
        self.timeout = timeout
        self.username = username

    #
    # ee2 params:
    # job_id: string
    # projection: list<string>
    #
    # ee2 result:
    #  job_id - string - id of the job
    # user - string - user who started the job
    # wsid - int - id of the workspace where the job is bound
    # authstrat - string - what strategy used to authenticate the job
    # job_input - object - inputs to the job (from the run_job call)  ## TODO - verify
    # updated - string - timestamp of the last time the status was updated
    # running - string - timestamp of when it entered the running state
    # created - string - timestamp when the job was created
    # finished - string - timestamp when the job was finished
    # status - string - status of the job. one of the following:
    #     created - job has been created in the service
    #     queued - job is queued to be run
    #     running - job is running on a worker node
    #     finished - job was completed successfully
    #     error - job is no longer running, but failed with an error
    #     terminated - job is no longer running, terminated either due to user cancellation,
    #                  admin cancellation, or some automated task
    # error_code - int - internal reason why the job is an error. one of the following:
    #     0 - unknown
    #     1 - job crashed
    #     2 - job terminated by automation
    #     3 - job ran over time limit
    #     4 - job was missing its automated output document
    #     5 - job authentication token expired
    # errormsg - string - message (e.g. stacktrace) accompanying an errored job
    # error - object - the JSON-RPC error package that accompanies the error code and message

    # terminated_code - int - internal reason why a job was terminated, one of:
    #     0 - user cancellation
    #     1 - admin cancellation
    #     2 - terminated by some automatic process
    #

    def raw_jobs_to_jobs(self, raw_jobs, services=None):
        if services is None:
            services = KBaseServices(config=self.config, token=self.token)
        if len(raw_jobs) == 0:
            return []

        # Collect up ids for related entities for batch queries.
        usernames = set()
        apps_to_fetch = dict()
        workspace_ids = set()

        stats = dict()
        start = time.time_ns()

        for raw_job in raw_jobs:
            usernames.add(raw_job['user'])

            if 'job_input' in raw_job:
                job_input = raw_job['job_input']
                if 'app_id' in job_input:
                    app = parse_app_id(job_input.get('app_id'), job_input.get('method'))
                    # note we save the parsed app id as 'app'
                    raw_job['app'] = app
                    if app is not None:
                        if app['type'] == 'narrative':
                            apps_to_fetch[app['id']] = app
                else:
                    raw_job['app'] = None

                if 'wsid' in raw_job:
                    workspace_ids.add(raw_job['wsid'])

        # Get a dict of unique users for this set of jobs
        users_map = services.get_users(list(usernames))

        stats['get_users'] = (time.time_ns() - start) / 1000000
        start = time.time_ns()

        # Get a dict of unique users for this set of jobs.
        apps = services.get_apps(list(apps_to_fetch.values()))

        stats['get_apps'] = (time.time_ns() - start) / 1000000
        start = time.time_ns()

        workspace_map = dict()
        workspaces = services.get_workspaces(list(workspace_ids))
        # print('GOT WORKSPACES', workspaces)
        for workspace in workspaces:
            # print(f'WORKSPACE?? {workspace["id"]}')
            workspace_map[workspace['id']] = workspace

        stats['get workspaces'] = (time.time_ns() - start) / 1000000
        start = time.time_ns()

        # Now join them all together.
        jobs = []
        for raw_job in raw_jobs:
            job = raw_job_to_job(raw_job, apps, users_map, workspace_map)
            jobs.append(job)

        stats['transform jobs'] = (time.time_ns() - start) / 1000000

        return jobs, stats

    def is_admin(self):
        api = EE2Api(url=self.config['ee2-url'], token=self.token, timeout=self.timeout)
        result = api.is_admin()
        if result == 1:
            return True
        else:
            return False

    def get_client_groups(self):
        api = EE2Api(url=self.config['ee2-url'], token=self.token, timeout=self.timeout)
        result = api.get_client_groups()
        return {
            'client_groups': result
        }

    def get_job_log(self, params):
        job_id = get_param(params, 'job_id')
        offset = get_param(params, 'offset')
        limit = get_param(params, 'limit')
        # search = params.get('search')
        # level = params.get('level')
        admin = params.get('admin', False)
        if admin:
            admin = 1
        else:
            admin = 0

        api = EE2Api(url=self.config['ee2-url'], token=self.token, timeout=self.timeout)
        try:
            # Note plural form of get_job_log. The upstream apis (njs, ee2 copying it)
            # mistakenly use the plural form ... it is a log of a job, not a logs of a job.
            result = api.get_job_logs({
                'job_id': job_id,
                'offset': offset,
                'limit': limit,
                'as_admin': admin})
        except ServiceError as se:
            # handle specific error mesages
            if se.code == -32000:
                if re.search('Cannot find job log with id[s]?:', se.message):
                    return {
                        'log': [],
                        'total_count': 0
                    }
                    # raise ServiceError(
                    #     code=30,
                    #     message='The requested job log could not be found',
                    #     data={
                    #         'job_id': job_id
                    #     })
            raise se
        else:
            entries = [raw_log_line_to_entry(line, index, offset)
                       for index, line in enumerate(result['lines'])]

            if limit is not None:
                entries = entries[slice(0, limit)]

            # entries = list(map(raw_log_line_to_entry, result['lines']))
            return {
                'log': entries,
                'total_count': result['count']
            }

    def cancel_job(self, params):
        api = EE2Api(url=self.config['ee2-url'], token=self.token, timeout=self.timeout)
        admin = params.get('admin', False)
        if admin:
            as_admin = 1
            terminated_code = params.get('code', 1)
        else:
            as_admin = 0
            terminated_code = params.get('code', 0)
        try:
            api.cancel_job({
                'job_id': params['job_id'],
                'terminated_code': terminated_code,
                'as_admin': as_admin
            })
            return {
                'canceled': True
            }
        except ServiceError as se:
            if re.search(('A job with status .+ cannot be terminated. '
                          'It is already cancelled.'), se.message):
                return {
                    'canceled': False
                }
            elif re.search('Cannot find job with ids:', se.message):
                raise ServiceError(code=10,
                                   message="The job specified for cancelation does not exist",
                                   data={
                                       'job_id': params['job_id']
                                   })
            else:
                raise se

    def ee2_query_jobs(self, offset, limit, time_span=None, search=None,
                       filter=None, sort=None, admin=False):
        # TODO: timeout global or timeout per call?
        api = EE2Api(url=self.config['ee2-url'], token=self.token, timeout=self.timeout)

        params = {
            'start_time': time_span['from'],
            'end_time': time_span['to'],
            'offset': offset,
            'limit': limit
        }

        if filter is not None:
            raw_query = []

            status = filter.get('status', [])
            if len(status) > 0:
                status_transform = {
                    'create': 'created',
                    'queue': 'queued',
                    'run': 'running',
                    'complete': 'completed',
                    'error': 'error',
                    'terminate': 'terminated'
                }
                # value = list(map(lambda x: status_transform.get(x, x), value))
                status = [status_transform.get(x, x) for x in status]
                raw_query.append({
                    'status': {
                        '$in': status
                    }
                })

            # parse and reformat the filters...
            workspace_id = filter.get('workspace_id', [])
            if len(workspace_id) > 0:
                raw_query.append({
                    'wsid': {
                        '$in': workspace_id
                    }
                })

            user = filter.get('user', [])
            if len(user) > 0:
                raw_query.append({
                    'user': {
                        '$in': user
                    }
                })

            client_group = filter.get('client_group', [])
            if len(client_group) > 0:
                raw_query.append({
                    'job_input.requirements.clientgroup': {
                        '$in': client_group
                    }
                })

            app_id = filter.get('app_id', [])
            if len(app_id) > 0:
                raw_query.append({
                    'job_input.app_id': {
                        '$in': app_id
                    }
                })

            app_module = filter.get('app_module', [])
            if len(app_module) > 0:
                raw_query.append({
                    '$or': [{'job_input.app_id': {'$regex': f'^{module_name}/', '$options': 'i'}}
                            for module_name in app_module]
                })

            app_function = filter.get('app_function', [])
            if len(app_function) > 0:
                raw_query.append({
                    '$or': [{'job_input.app_id': {'$regex': f'/{function_name}$', '$options': 'i'}}
                            for function_name in app_function]
                })

            # wrap it in a raw query for mongoengine
            # TODO: upstream ee2 service should not be exposed like this!
            if len(raw_query) > 0:
                filter_query = {
                    '__raw__': {
                        '$and': raw_query
                    }
                }

                params['filter'] = filter_query

        if sort is not None:
            # sort specs are not supported for ee2 (for now)
            # rather sorting is always by created timestamp
            # defaulting to ascending but reversable with the
            # ascending parameter set to 0.
            if len(sort) == 0:
                pass
            elif len(sort) > 1:
                raise ServiceError(code=40000, message="Only one sort spec supported",
                                   data={})
            elif sort[0].get('key') != 'created':
                raise ServiceError(
                    code=40000, message="The sort spec must be for the 'created' key")

            if sort[0].get('direction') == 'ascending':
                ascending = 1
            else:
                ascending = 0
            params['ascending'] = ascending

        try:
            if admin:
                result = api.check_jobs_date_range_for_all(params)
            else:
                result = api.check_jobs_date_range_for_user(params)
            return result['jobs'], result['query_count']
        except ServiceError:
            raise
        except Exception as ex:
            raise ServiceError(code=40000, message='Unknown error', data={
                'original_message': str(ex)
            })

    def query_jobs(self, params):
        stats = dict()
        start = time.time_ns()
        raw_jobs, found_count = self.ee2_query_jobs(
            offset=params['offset'],
            limit=params['limit'],
            filter=params.get('filter'),
            search=params.get('search'),
            sort=params.get('sort'),
            time_span=params.get('time_span', None),
            admin=params.get('admin', False)
        )
        stats['query_jobs'] = (time.time_ns() - start) / 1000000
        start = time.time_ns()
        # The total count is not returned by ee2 a this time;
        total_count = found_count

        if len(raw_jobs) == 0:
            return [], 0, total_count, stats

        jobs, stats2 = self.raw_jobs_to_jobs(raw_jobs)

        stats['raw_jobs_to_jobs'] = (time.time_ns() - start) / 1000000

        # Now DONE!
        return jobs, found_count, total_count, {**stats, **stats2}

    def ee2_get_jobs(self, params):
        api = EE2Api(url=self.config['ee2-url'], token=self.token, timeout=self.timeout)
        if params.get('admin', False):
            as_admin = True
        else:
            as_admin = True

        try:
            jobs = api.check_jobs({
                'job_ids': params['job_ids'],
                'as_admin': as_admin
            })
            return jobs['job_states']
        except ServiceError as se:
            if se.code == -32000:
                if re.search('Cannot find job with ids:', se.message):
                    # Hmm, wonder if the missing job ids are returned in the exception?
                    raise ServiceError(
                        code=10,
                        message='Job not found',
                        data={
                            'message': se.message
                        })
                else:
                    raise ServiceError(
                        code=1,
                        message='Unknown error occurred',
                        data={
                            'upstream_error': {
                                'code': se.code,
                                'message': se.message,
                                'data': se.data
                            }
                        })
            else:
                raise
        except Exception as ex:
            raise ServiceError(
                code=1,
                message='Unknown error',
                data={
                    'original_message': str(ex)
                })

    def get_jobs(self, params):
        if len(params['job_ids']) == 0:
            return [], {}

        stats = dict()
        start = time.time_ns()

        raw_jobs = self.ee2_get_jobs(params)

        stats['ee2_get_jobs'] = (time.time_ns() - start) / 100000
        start = time.time_ns()

        jobs, stats2 = self.raw_jobs_to_jobs(raw_jobs)

        stats['raw_jobs_to_jobs'] = (time.time_ns() - start) / 1000000

        return jobs,  {**stats, **stats2}
