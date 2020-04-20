from biokbase.Errors import ServiceError
from JobBrowserBFF.model.EE2Api import EE2Api
from JobBrowserBFF.model.KBaseServices import KBaseServices
from JobBrowserBFF.Utils import parse_app_id
import re
import json


def get_param(params, key):
    if key not in params:
        raise ValueError(f'required param {key} not provided')
    return params.get(key)


def raw_job_to_state(raw_job):
    raw_state = raw_job['status']

    # which queue it is/was running on.
    client_group = find_in(['job_input', 'requirements', 'clientgroup'], raw_job, 'njs')

    if raw_state == 'created':
        return {
            'status': 'create',
            'create_at': raw_job['created'],
            'client_group': client_group
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
            # TODO: queued time does not exist yet!
            'queue_at': raw_job['created'],
            'run_at': raw_job['running'],
            'client_group': client_group
        }
    elif raw_state == 'completed':
        return {
            'status': 'complete',
            'create_at': raw_job['created'],
            # TODO: queued time does not exist yet!
            'queue_at': raw_job['created'],
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
            # TODO: queued time does not exist yet!
            # 'queue_at': iso_to_ms(raw_job['created']),
            # TODO: remove the usage of 'updated' when this is fixed.
            'finish_at': raw_job.get('finished', raw_job.get('updated', None)),
            'error': {
                'code': 1,
                'message': raw_job.get('errormsg', '')
            },
            'client_group': client_group
        }

        # TODO: when 'queued' is ready
        if 'queued' in raw_job:
            state['queue_at'] = raw_job['queued']

        if 'running' in raw_job:
            # remove when queued is ready.
            state['queue_at'] = raw_job['created']
            state['run_at'] = raw_job['running']
        return state
    elif raw_state == 'terminated':
        state = {
            'status': 'terminate',
            'create_at': raw_job['created'],
            # TODO: queued time does not exist yet!
            'queue_at': raw_job['created'],
            # TODO: finished time is mysteriously missing!
            'finish_at': raw_job['updated'],
            'reason': {
                'code': 0
            },
            'client_group': client_group
        }
        # reason omitted because not supported by kb_Metrics
        if 'running' in raw_job:
            state['run_at'] = raw_job['running']

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
    # client_group = None
    if app is not None:
        app_info = apps_map.get(app['id'], None)

        if app_info is None:
            app['title'] = app['id']
            app['client_groups'] = []
        else:
            app['title'] = app_info['name']
            app['client_groups'] = app_info['client_groups']
            # if len(app['client_groups']) > 0:
            #     client_group = app['client_groups'][0]

     # Get the additional workspace info out of the workspaces map, and
    # also handle multiple types of workspace
    if 'job_input' in raw_job:
        job_input = raw_job['job_input']

        # Determine workspace type
        workspace_id = job_input.get('wsid', None)
        if workspace_id is None:
            workspace = None
            job_type = 'unknown'
        else:
            workspace = workspaces_map.get(workspace_id, None)
            if workspace is None:
                job_type = 'unknown'
            elif workspace['is_accessible']:
                if workspace.get('narrative'):
                    job_type = 'narrative'
                elif app is not None and 'export' in app['function_name']:
                    job_type = 'export'
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

    def raw_jobs_to_jobs(self, raw_jobs):
        if len(raw_jobs) == 0:
            return []

        # Collect up ids for related entities for batch queries.
        usernames = set()
        apps_to_fetch = dict()
        workspace_ids = set()

        for raw_job in raw_jobs:
            usernames.add(raw_job['user'])

            if 'job_input' in raw_job:
                job_input = raw_job['job_input']
                if 'app_id' in job_input:
                    app = parse_app_id(job_input['app_id'])
                    # note we save the parsed app id as 'app'
                    raw_job['app'] = app
                    if app is not None:
                        apps_to_fetch[app['id']] = app
                else:
                    raw_job['app'] = None

                if 'wsid' in raw_job:
                    workspace_ids.add(raw_job['wsid'])

        services = KBaseServices(config=self.config, token=self.token)

        # Get a dict of unique users for this set of jobs
        users_map = services.get_users(list(usernames))

        # Get a dict of unique users for this set of jobs.
        apps_map = dict()
        apps = services.get_apps(list(apps_to_fetch.values()))
        for app_id, app in apps.items():
            if app is not None:
                apps_map[app_id] = app

        workspace_map = dict()
        workspaces = services.get_workspaces(list(workspace_ids))
        for workspace in workspaces:
            workspace_map[workspace['id']] = workspace

        # Now join them all together.
        jobs = []
        for raw_job in raw_jobs:
            try:
                job = raw_job_to_job(raw_job, apps_map, users_map, workspace_map)
                jobs.append(job)
            except Exception as ex:
                print('Error converting job: ' + str(ex))

        return jobs

    def is_admin(self):
        api = EE2Api(url=self.config['ee2-url'], token=self.token, timeout=self.timeout)
        try:
            result = api.is_admin()
            if result == 1:
                return True
            else:
                return False
        except ServiceError as se:
            raise se
        # TODO: is this implemented yet?

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
            params['filter'] = filter

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

    def filter_transform(self, raw_filter):
        field_name_transforms = {
            'workspace_id': 'wsid',
        }
        # yeah, doing this with map is just ugly.
        filter = dict()
        for field, value in raw_filter.items():
            # transform the field name from ours to the idiosyncratic upstream names.
            field_name = field_name_transforms.get(field, field)

            # transform field values
            if field_name == 'status':
                status_transform = {
                    'create': 'created',
                    'queue': 'queued',
                    'run': 'running',
                    'complete': 'completed',
                    'error': 'error',
                    'terminate': 'terminated'
                }
                value = list(map(lambda x: status_transform.get(x, x), value))

            field_name = field_name + '__in'
            filter.update({
                field_name: value
            })
        return filter

    def query_jobs(self, params):
        # Sort is required (and validated before we get here) so safe to assume it exists.
        # but it isn't implemented yet on the upstream service?

        # Search is optional.

        # Filter is optional.
        if 'filter' in params:
            # Some upstream field names are not api-friendly (imo)
            filter = self.filter_transform(params['filter'])
        else:
            # Note, we can use None for optional params.
            filter = None

        if 'search' in params:
            search = params['search']
        else:
            search = None

        # TODO: massage the sort?
        sort = params.get('sort', None)

        raw_jobs, found_count = self.ee2_query_jobs(
            offset=params['offset'],
            limit=params['limit'],
            filter=filter,
            search=search,
            sort=sort,
            time_span=params.get('time_span', None),
            admin=params.get('admin', False)
        )
        # The total count is not returned by ee2 a this time;
        total_count = found_count

        if len(raw_jobs) == 0:
            return [], 0, total_count

        jobs = self.raw_jobs_to_jobs(raw_jobs)

        # Now DONE!
        return jobs, found_count, total_count

    def query_jobs_admin(self, params):
        # Sort is required (and validated before we get here) so safe to assume it exists.
        # but it isn't implemented yet on the upstream service?

        # Search is optional.

        # Filter is optional.
        if 'filter' in params:
            # Some upstream field names are not api-friendly (imo)
            field_name_transforms = {
                'workspace_id': 'wsid',
            }
            # yeah, doing this with map is just ugly.
            filter = {}
            for field, value in params['filter'].items():
                # transform the field name from ours to the idiosyncratic upstream names.
                field_name = field_name_transforms.get(field, field)
                # filter.append("{}={}".format(field_name, value))
                filter.update({
                    field_name: value
                })
        else:
            # Note, we can use None for optional params.
            filter = None

        # TODO: massage the sort?
        sort = params.get('sort', None)

        raw_jobs, found_count = self.ee2_query_jobs(
            offset=params['offset'],
            limit=params['limit'],
            filter=filter,
            sort=sort,
            time_span=params.get('time_span', None),
            admin=True
        )

        total_count = found_count

        if len(raw_jobs) == 0:
            return [], 0, total_count

        jobs = self.raw_jobs_to_jobs(raw_jobs)

        return jobs, found_count, total_count

    def ee2_get_jobs(self, params):
        api = EE2Api(url=self.config['ee2-url'], token=self.token, timeout=self.timeout)

        try:
            jobs = api.check_jobs({
                'job_ids': params['job_ids']
            })
            # print('JOBS JOBS JOBS', jobs)
            # TODO: when jobs returned as a array, remove this workaround.
            # jobs = []
            # for job_id, job_info in job_map.items():
            #     jobs.append(job_info)

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
            return []

        raw_jobs = self.ee2_get_jobs(params)

        return self.raw_jobs_to_jobs(raw_jobs)
