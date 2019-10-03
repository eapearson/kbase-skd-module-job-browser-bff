from biokbase.DynamicServiceClient import DynamicServiceClient
from biokbase.GenericClient import GenericClient
from biokbase.Errors import ServiceError
import requests

def raw_job_to_job(raw_job, app_info, user, workspace):
    # Get the user
    realname = user or raw_job['user']

    state = raw_job['state']
    if state == 'FINISHED':
        state = 'COMPLETED'
    state = state.lower()

    # parse out app.
    if 'app_id' in raw_job:
        [module_name, function_name] = raw_job['app_id'].split('/')
        if app_info is not None:
            app_title = app_info['name']
        else:
            app_title = 'Unknown'
        app = {
            'module_name': module_name,
            'function_name': function_name,
            'title': app_title
        }
    else:
        app = None

    if workspace is None:
        job_type = 'unknown'
    elif workspace['is_narrative']:
        job_type = 'narrative'
    elif app is not None and 'export' in app['function_name']:
        job_type = 'export'
    else:
        job_type = 'workspace'

    if job_type == 'narrative':
        job = {
            'job_id': raw_job['job_id'],
            'type': job_type,
            'status': state,
            'queued_at': raw_job.get('creation_time'),
            'started_at': raw_job.get('exec_start_time'),
            'finished_at': raw_job.get('finish_time'),
            'owner': {
                'username': raw_job['user'],
                'realname': realname
            },
            'narrative': {
                'workspace_id': int(raw_job['wsid']),
                'workspace_name': raw_job['workspace_name'],
                'title': raw_job['narrative_name'],
                "is_deleted": raw_job['narrative_is_deleted']
            },
            'app': app,
            'client_groups': raw_job['client_groups']
        }
    elif job_type == 'export':
        job = {
            'job_id': raw_job['job_id'],
            'type': job_type,
            'status': state,
            'queued_at': raw_job.get('creation_time'),
            'started_at': raw_job.get('exec_start_time'),
            'finished_at': raw_job.get('finish_time'),
            'owner': {
                'username': raw_job['user'],
                'realname': realname
            },
            'app': app,
            'client_groups': raw_job['client_groups']
        }
    elif job_type == 'workspace':
        job = {
            'job_id': raw_job['job_id'],
            'type': job_type,
            'status': state,
            'queued_at': raw_job.get('creation_time'),
            'started_at': raw_job.get('exec_start_time'),
            'finished_at': raw_job.get('finish_time'),
            'owner': {
                'username': raw_job['user'],
                'realname': realname
            },
            'workspace': {
                'workspace_id': int(raw_job['wsid']),
                'workspace_name': raw_job['workspace_name']
            },
            'app': app,
            'client_groups': raw_job['client_groups']
        }
    else:
        job = {
            'job_id': raw_job['job_id'],
            'type': job_type,
            'status': state,
            'queued_at': raw_job.get('creation_time'),
            'started_at': raw_job.get('exec_start_time'),
            'finished_at': raw_job.get('finish_time'),
            'owner': {
                'username': raw_job['user'],
                'realname': realname
            },
            'app': app,
            'client_groups': raw_job['client_groups']
        }
    return job

def raw_log_line_to_entry(raw_log_line, entry_number):
    if raw_log_line.get('is_error', False):
        level = 'error'
    else:
        level = 'normal'
    return {
        'entry_number': entry_number,
        'entry': raw_log_line['line'],
        'level': level
    }
    
class Model(object):
    def __init__(self, config=None, token=None, username=None):
        self.config = config
        self.token = token
        self.username = username

    def get_job(self, job_id):
        url = self.config['srv-wiz-url']
        rpc = DynamicServiceClient(url=url,
                                   module='kb_Metrics',
                                   token=self.token)
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

    def is_metrics_admin(self):
        url = self.config['srv-wiz-url']
        rpc = DynamicServiceClient(url=url,
                                   module='kb_Metrics',
                                   token=self.token)
        try:
            result = rpc.call_func('is_admin', {})
            return result['is_admin']
        except ServiceError:
            raise
        except Exception as ex:
            raise ServiceError(code=40000, message='Unknown error', data={
                'original_message': str(err)
                })

    def query_jobs(self, current_user, users=None, offset=None, limit=None, date_range=None):
        url = self.config['srv-wiz-url']
        rpc = DynamicServiceClient(url=url,
                                   module='kb_Metrics',
                                   token=self.token)

        if not self.is_metrics_admin():
            users = [current_user]
        elif users is None:
            users = []

        try:
            params = {
                'user_ids': users,
                'offset': offset,
                'limit': limit
            }

            if (date_range):
                params['epoch_range'] = [date_range['from'], date_range['to']]

            jobs = rpc.call_func('query_jobs', params)

            return {
                'jobs': jobs['job_states'],
                'total_count': jobs['total_count']
            }
        except ServiceError:
            raise
        except Exception as ex:
            raise ServiceError(code=40000, message='Unknown error', data={
                'original_message': str(err)
                })

    def get_users(self, user_ids):
        url = self.config['auth-url']

        header = {
            'Accept': 'application/json',
            'Authorization': self.token,
        }

        endpoint = url + '/api/V2/users/?list=' + ','.join(user_ids)

        response = requests.get(endpoint, headers=header, timeout=10)
        if response.status_code != 200:
            raise ServiceError(code=40000, message='Error fetching users', data={'user_id': user_ids})
        else:
            try:
                result = response.json()
                return result
            except Exception as err:
                raise ServiceError(code=40000, message='Bad response', data={'user_id': user_ids, 'original_message': str(err)})

    def get_apps(self, app_ids):
        url = self.config['nms-url']

        rpc = GenericClient(url=url, module="NarrativeMethodStore", token=self.token)
        
        result = rpc.call_func('get_method_brief_info', {
            'ids': app_ids
        })

        return result

    def get_workspaces(self, workspace_ids):
        url = self.config['workspace-url']
        rpc = GenericClient(url=url, module="Workspace", token=self.token)

        result = []

        for workspace_id in workspace_ids:
            [id, name, owner, moddate, max_objid, user_permission, globalread, lockstat, metadata] = rpc.call_func('get_workspace_info', {
                'id': workspace_id
            })

            if metadata.get('narrative', None) is None:
                is_narrative = False
            else:
                is_narrative = True

            info = {
                'id': id,
                'name': name,
                'is_narrative': is_narrative                
            }
            if (is_narrative):
                if metadata.get('is_temporary', None) == 'true':
                    is_temporary = True
                else:
                     is_temporary = False
                info['narrative'] = {
                    'narrative_title': metadata.get('narrative_nice_name', None),
                    'is_temporary': is_temporary
                }

            result.append(info)

        return result

    def get_client_groups(self):
        url = self.config['catalog-url']
        rpc = GenericClient(url=url, module="Catalog", token=self.token)
        # Note that an empty params is sent - this is due to the definition of this
        # catalog method -- it is specified with an empty struct as the param!
        result = rpc.call_func('get_client_groups', {})
        return result

    def get_job_log(self, job_id, offset=None, limit=None, search=None, level=None):
        url = self.config['njsw-url']

        rpc = GenericClient(url=url, module="NarrativeJobService", token=self.token)

        result = rpc.call_func('get_job_logs', {
            'job_id': job_id,
            'skip_lines': offset
        })

        entries = [raw_log_line_to_entry(line, index) for index, line in enumerate(result['lines'])]

        # entries = list(map(raw_log_line_to_entry, result['lines']))
        return {
            'log': entries,
            'total_count': len(result['lines'])
        }

    def cancel_job(self, job_id):
        url = self.config['njsw-url']

        rpc = GenericClient(url=url, module="NarrativeJobService", token=self.token)

        result = rpc.call_func('cancel_job', {
            'job_id': job_id
        })

        return True


