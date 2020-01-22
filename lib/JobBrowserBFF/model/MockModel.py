from biokbase.DynamicServiceClient import DynamicServiceClient
from biokbase.GenericClient import GenericClient
from biokbase.Errors import ServiceError
from JobBrowserBFF.model.KBaseServices import KBaseServices
from JobBrowserBFF.Utils import ms_to_iso, iso_to_ms, parse_app_id
import requests
import re
import glob
import os
import json
import pymongo
import urllib.parse
from bson import json_util


def raw_log_entry_to_entry(raw_log_entry, entry_number, offset):
    if raw_log_entry.get('is_error', False):
        level = 'error'
    else:
        level = 'normal'
    row_number = entry_number + offset
    if 'ts' in raw_log_entry:
        logged_at = raw_log_entry['ts']
    else:
        logged_at = row_number
    return {
        'row': row_number,
        'logged_at': logged_at,
        'message': raw_log_entry['message'],
        'level': level
    }
    
class MockModel(object):
    def __init__(self, config, token, timeout, username):
        self.config = config
        self.token = token
        self.timeout = timeout
        self.username = username
        mongo = pymongo.MongoClient('mongo',
                                    username='test',
                                    password=urllib.parse.quote_plus('test'),
                                    authSource='admin',
                                    authMechanism='SCRAM-SHA-256')
        self.db = mongo['JobBrowserBFF']

    # TODO: mock tokens should be in the db
    # TODO: need to be able to stuff tokens into the mock db, since we may need
    # to use real tokens in order to do stuff like call to the CI workspace
    def is_admin(self):
        token = self.token
        if self.token == 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA':
            return True
        elif self.token == 'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB':
            return False
        else:
            raise Exception('Unexpected mock condition: token not supported: {}'.format(self.token))

    # def get_job(self, job_id):
    #     jobs_collection = db['jobs']
    #     filter = {
    #         'job_id': job_id
    #     }

    #     # TODO: filter on username and check if admin.
    #     result = json.loads(json_util.dumps(jobs_collection.find(filter)))
    #     if len(result) == 0:
    #         return None
        
    #     return result[0]

    def fix_workspaces(self, jobs):
        # Now find any workspaces and get info for them (given the current user)
        
        workspace_ids = set()
        for job in jobs:
            if not job['context'].get('workspace'):
                continue 
            workspace_id = job['context']['workspace'].get('id')
            if workspace_id:
                workspace_ids.add(workspace_id)

        # Get a map of workspace info
        # Note that an inaccessible workspace will be marked as such.
        # See the spec for the structure of JobContext and KBaseServices.py for
        # the return structure from get_workspaces, which is the same
        # (by design)
        workspaces_map = dict()
        services = KBaseServices(config=self.config, token=self.token)
        workspaces = services.get_workspaces(list(workspace_ids))
        for workspace in workspaces:
            workspaces_map[workspace['id']] = workspace

        # Now rebuild the job context based on these results.
        for job in jobs:
            # Determine the job type: narrative, workspace, export, unknown.
            # No workspace, could be export, or unknown.
            if not job['context'].get('workspace'):
                if job.get('app') and 'export' in job['app']['function_name']:
                    # elif app is not None and 'export' in app['function_name']:
                    job_type = 'export'
                else:
                    job_type = 'unknown'
            else:
                workspace_id = job['context']['workspace']['id']
                workspace = workspaces_map.get(workspace_id, None)

                # if workspace_id == 43676:
                print('WORKSPACE', workspace, job)

                if workspace['is_accessible']:
                    if workspace.get('narrative'):
                        job_type = 'narrative'
                    elif job.get('app') and 'export' in job['app'].get('function_name', ''):
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
            job['context'] = context

    def query_jobs(self, params):
        jobs_collection = self.db['jobs']

        is_admin = params.get('admin', False)

        filters = []

        # Enforce the single user model if not admin.
        if is_admin:
            if not self.is_admin():
                raise ServiceError(
                    code=50,
                    message='Permission denied for this operation',
                    data={})
        else:
            filters.append({
                'owner.username': self.username
            })

        # Get the total # jobs for this user, as the "total_count"
        if len(filters) > 0:
            cursor = jobs_collection.find({'$and': filters})
            total_count = cursor.count()
        else:
            total_count = jobs_collection.count()

        # Apply the time range.
        filters.append({'$and': [
            {'state.create_at': {'$gte': params['time_span']['from']}},
            {'state.create_at': {'$lt': params['time_span']['to']}}
        ]})
    
        # Handle field-specific filters
        if 'filter' in params:
            for key, value in params['filter'].items():
                if key == 'status':
                    filters.append({'state.status': value})
                elif key == 'app':
                    # filters.append({'$or': [
                    #     {'app.function_name': value},
                    #     {'app.module_name': value}
                    # ]})
                    filters.append({'app.id': value})
                elif key == 'workspace_id':
                    filters.append({'context.workspace.id': value})
                elif key == 'job_id':
                    filters.append({'job_id': value})
                elif key == 'client_group':
                    filters.append({'state.client_group': value})
                    
        # Handle free-text search
        if 'search' in params:
            term_expressions = []
            for term in params['search']['terms']:
                term_expressions.append({
                    '$or': [
                        {'job_id': {'$regex': term, '$options': 'i'}},
                        {'app.id': {'$regex': term, '$options': 'i'}},
                        {'state.status': {'$regex': term, '$options': 'i'}},
                        {'state.client_group': {'$regex': term, '$options': 'i'}},
                        {'owner.username': {'$regex': term, '$options': 'i'}},
                        {'msg': {'$regex': term, '$options': 'i'}}
                    ]
                })
            filters.append({'$and': term_expressions})

        # Put it all together and do it.
        query = {'$and': filters}
        cursor = jobs_collection.find(query, {'_id': False})
        found_count = cursor.count()

        # Handle sorting.
        if 'sort' in params:
            sort = []
            for sort_spec in params['sort']:
                key = sort_spec['key']
                direction = sort_spec['direction']

                if direction == 'ascending':
                    sort_direction = 1
                else:
                    sort_direction = -1

                if key == 'created':
                    sort_key = 'state.create_at'

                sort.append((sort_key, sort_direction))
            cursor.sort(sort)

        cursor.skip(params['offset'])
        cursor.limit(params['limit'])
                                   
        # TODO: filter on username and check if admin.
        jobs = json.loads(json_util.dumps(cursor))

        # Fix up workspace info relative to the current user.
        self.fix_workspaces(jobs)

        
        return jobs, found_count, total_count

    def get_jobs(self, params):
        jobs_collection = self.db['jobs']

        filters = []

        if params.get('admin', False):
            if not self.is_admin():
                raise ServiceError(
                    code=50,
                    message='Permission denied for this operation',
                    data={})
        else:
            filters.append({
                'owner.username': self.username
            })

        filters.append({
            'job_id': {'$in': params['job_ids']}  
        })

        query = {'$and': filters}
        cursor = jobs_collection.find(query, {'_id': False})
        jobs = json.loads(json_util.dumps(cursor))
        return jobs

    def get_users(self, user_ids):
        url = self.config['auth-url']

        header = {
            'Accept': 'application/json',
            'Authorization': self.token,
        }

        endpoint = url + '/api/V2/users/?list=' + ','.join(user_ids)

        response = requests.get(endpoint, headers=header, timeout=self.timeout/1000)
        if response.status_code != 200:
            raise ServiceError(code=40000, message='Error fetching users', data={'user_id': user_ids})
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
                raise ServiceError(code=40000, message='Bad response', data={'user_id': user_ids, 'original_message': str(err)})

    def get_client_groups(self):
        url = self.config['catalog-url']
        rpc = GenericClient(url=url, module="Catalog", token=self.token)
        # Note that an empty params is sent - this is due to the definition of this
        # catalog method -- it is specified with an empty struct as the param!
        result = rpc.call_func('get_client_groups', {})
        return result

    def get_job(self, job_id):
        # First, get the job and ensure the user has access to the logs.
        jobs_collection = self.db['jobs']
        raw_job = jobs_collection.find_one({
            'job_id': job_id
        }, {'_id': False})

        if raw_job is None:
            raise ServiceError(
                code=10,
                message='Job {} could not be found'.format(job_id),
                data={
                    'job_id': job_id
                }
            )
        
        job = json.loads(json_util.dumps(raw_job))
        if job['owner']['username'] != self.username:
            raise ServiceError(
                code=40,
                message='Access denied to job {}'.format(job_id),
                data={
                    'job_id': job_id,
                    'username': self.username
                }
            )

        return job


    def get_job_log(self, job_id, offset, limit, search=None, level=None):
        # TODO: enforce perms

        # First, get the job and ensure the user has access to the logs.
        jobs_collection = self.db['jobs']
        raw_job = jobs_collection.find_one({
            'job_id': job_id
        }, {'_id': False})

        if raw_job is None:
            raise ServiceError(
                code=10,
                message='Job {} could not be found'.format(job_id),
                data={
                    'job_id': job_id
                }
            )
        
        job = json.loads(json_util.dumps(raw_job))
        if job['owner']['username'] != self.username:
            raise ServiceError(
                code=40,
                message='Access denied to job {}'.format(job_id),
                data={
                    'job_id': job_id,
                    'username': self.username
                }
            )

        # Now get the logs
        logs_collection = self.db['job_logs']
        filters = []
        filters.append({
            'job_id': job_id
        })
        cursor = logs_collection.find({'$and': filters})
        total_count = cursor.count()
        cursor.sort([('id', 1)])
        cursor.skip(offset)
        cursor.limit(limit)

        log = json.loads(json_util.dumps(cursor))

        entries = [raw_log_entry_to_entry(line, index, offset) for index, line in enumerate(log)]

        return {
            'job': job,
            'log': entries,
            'total_count': total_count
        }

    def cancel_job(self, job_id):
        job = self.get_job(job_id)

        if job['state']['status'] not in ['create', 'queue', 'run']:
            return ServiceError(
                code=60,
                message='Job is not cancelable',
                data={
                    'job_id': job_id,
                    'job_status': job['state']['status']
                }
            )

