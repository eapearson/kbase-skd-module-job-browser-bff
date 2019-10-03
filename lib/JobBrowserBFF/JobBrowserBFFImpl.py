# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import re
from JobBrowserBFF.Validation import Validation
from JobBrowserBFF.Model import Model, raw_job_to_job
from JobBrowserBFF.definitions.Definitions import Definitions
#END_HEADER


class JobBrowserBFF:
    '''
    Module Name:
    JobBrowserBFF

    Module Description:
    A KBase module: JobBrowserBFF
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = ""
    GIT_COMMIT_HASH = "HEAD"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        
        self.validation = Validation(load_schemas=True)
        self.definitions = Definitions(load=True)

        self.validation.validate_config(config)
        self.config = config
        #END_CONSTRUCTOR
        pass


    def get_jobs(self, ctx, params):
        """
        :param params: instance of type "GetJobsParams" (****************** *
           get_jobs ******************) -> structure: parameter "job_ids" of
           list of type "JobID" (Core types)
        :returns: instance of type "GetJobsResult" -> structure: parameter
           "jobs" of list of type "JobInfo" -> structure: parameter "job_id"
           of type "JobID" (Core types), parameter "type" of type "JobType"
           (narrative, export, workspace, unknown), parameter "owner" of type
           "User" -> structure: parameter "UserID" of String, parameter
           "realname" of String, parameter "status" of type "JobStatus"
           (queued, running, completed, errored_queued, errored_running,
           canceled_queued, canceled_running), parameter "queued_at" of type
           "epoch_time", parameter "started_at" of type "epoch_time",
           parameter "finished_at" of type "epoch_time", parameter "app" of
           type "AppInfo" -> structure: parameter "module_name" of String,
           parameter "function_name" of String, parameter "title" of String,
           parameter "narrative" of type "NarrativeInfo" -> structure:
           parameter "workspace_id" of Long, parameter "workspace_name" of
           String, parameter "title" of String, parameter "is_deleted" of
           type "bool" (Type synonym conveniences), parameter "client_groups"
           of list of type "ClientGroup" (njs, bigmem, bigmemlong, kb_import,
           ...)
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN get_jobs
        self.validation.validate_params('get_jobs', params)

        # ecall to kb_Metrics.get_job to get the raw job info
        model = Model(config=self.config,
                      token=ctx['token'],
                      username=ctx['user_id'])

        jobs = []

        # Where possible we do a batch request.
        usernames = set()
        app_ids = set()
        raw_jobs = []

        for job_id in params['job_ids']:
            raw_job = model.get_job(job_id=job_id)

            usernames.add(raw_job['user'])
            app_ids.add(raw_job['app_id'])
            raw_jobs.append(raw_job)

        # Get a dict of unique users for this set of jobs
        users_map = model.get_users(list(usernames))

        # Get a dict of unique apps for this set of jobs.
        apps_map = dict()
        apps = model.get_apps(list(app_ids))
        for app in apps:
            apps_map[app['id']] = app

        # Now join them all together.
        for raw_job in raw_jobs:
            job = raw_job_to_job(raw_job, apps_map[raw_job['app_id']], users_map[raw_job['user']])
            jobs.append(job)

        result = {
            'jobs': jobs
        }
        self.validation.validate_result('get_jobs', result)

        #END get_jobs

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method get_jobs return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def query_jobs(self, ctx, params):
        """
        :param params: instance of type "QueryJobsParams" -> structure:
           parameter "users" of list of type "UserID", parameter "jobs" of
           list of type "JobID" (Core types), parameter "sort" of list of
           type "SortSpec" -> structure: parameter "key" of type "SortKey"
           (behaves as an enum: narrative, app, submitted, status), parameter
           "direction" of type "SortDirection" (behaves as an enum:
           ascending, descending), parameter "search" of type "SearchSpec" ->
           structure: parameter "terms" of list of String, parameter
           "date_range" of type "DateRangeSpec" -> structure: parameter
           "from" of type "epoch_time", parameter "to" of type "epoch_time",
           parameter "client_groups" of list of type "ClientGroup" (njs,
           bigmem, bigmemlong, kb_import, ...), parameter "offset" of Long,
           parameter "limit" of Long
        :returns: instance of type "QueryJobsResult" -> structure: parameter
           "jobs" of list of type "JobInfo" -> structure: parameter "job_id"
           of type "JobID" (Core types), parameter "type" of type "JobType"
           (narrative, export, workspace, unknown), parameter "owner" of type
           "User" -> structure: parameter "UserID" of String, parameter
           "realname" of String, parameter "status" of type "JobStatus"
           (queued, running, completed, errored_queued, errored_running,
           canceled_queued, canceled_running), parameter "queued_at" of type
           "epoch_time", parameter "started_at" of type "epoch_time",
           parameter "finished_at" of type "epoch_time", parameter "app" of
           type "AppInfo" -> structure: parameter "module_name" of String,
           parameter "function_name" of String, parameter "title" of String,
           parameter "narrative" of type "NarrativeInfo" -> structure:
           parameter "workspace_id" of Long, parameter "workspace_name" of
           String, parameter "title" of String, parameter "is_deleted" of
           type "bool" (Type synonym conveniences), parameter "client_groups"
           of list of type "ClientGroup" (njs, bigmem, bigmemlong, kb_import,
           ...)
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN query_jobs
        self.validation.validate_params('query_jobs', params)

        model = Model(config=self.config,
                      token=ctx['token'],
                      username=ctx['user_id'])

        result = model.query_jobs(
            current_user = ctx['user_id'],
            users=params.get('users', None),
            offset=params.get('offset', 0),
            limit=params.get('limit', 10),
            date_range=params.get('date_range', None)
        )

        raw_jobs = result['jobs']
        total_count = result['total_count']

        # Where possible we do a batch request.
        usernames = set()
        app_ids = set()
        workspace_ids = set()

        for raw_job in raw_jobs:
            usernames.add(raw_job['user'])
            if 'app_id' in raw_job:
                app_ids.add(raw_job['app_id'])
            if 'wsid' in raw_job:
                workspace_ids.add(raw_job['wsid'])

        # Get a dict of unique users for this set of jobs
        users_map = model.get_users(list(usernames))

        # Get a dict of unique users for this set of jobs.
        apps_map = dict()
        apps = model.get_apps(list(app_ids))
        for app in apps:
            apps_map[app['id']] = app

        workspace_map = dict()
        workspaces = model.get_workspaces(list(workspace_ids))
        for workspace in workspaces:
            workspace_map[workspace['id']] = workspace
        
        # Now join them all together.
        jobs = []
        for raw_job in raw_jobs:
            if 'app_id' in raw_job:
                app = apps_map.get(raw_job['app_id'], None)
            else:
                app = None
            user = users_map.get(raw_job['user'], None)
            workspace = workspace_map.get(raw_job.get('wsid', None), None)
            job = raw_job_to_job(raw_job, app, user, workspace)
            jobs.append(job)

        # Now apply filtering
        if 'search' in params:
            filter = map(lambda x: re.compile(x, re.IGNORECASE), params['search'])
            filtered_jobs = []
            for job in jobs:
                for expr in filter:
                    if (re.search(expr, job['owner']['realname']) or
                        re.search(expr, re.job['app']['title']) or
                        re.search(expr, re.job['narrative']['title'])):
                        filtered_jobs.append(job)
        else:
            filtered_jobs = jobs

        # Now apply sorting
        # TODO: do sorting!

        # Now DONE!

        result = {
            'jobs': filtered_jobs,
            # TODO: this is a lie
            'total_count': total_count
        }

        self.validation.validate_result('query_jobs', result)
        #END query_jobs

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method query_jobs return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def get_job_log(self, ctx, params):
        """
        :param params: instance of type "GetJobLogParams" -> structure:
           parameter "job_id" of type "JobID" (Core types), parameter
           "search" of type "SearchSpec" -> structure: parameter "terms" of
           list of String, parameter "level" of list of type "LogLevel"
           (enum-like: default, error), parameter "offset" of Long, parameter
           "limit" of Long
        :returns: instance of type "GetJobLogResult" -> structure: parameter
           "log" of list of type "LogEntry" -> structure: parameter
           "entry_number" of Long, parameter "entry" of String, parameter
           "level" of type "LogLevel" (enum-like: default, error)
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN get_job_log
        self.validation.validate_params('get_job_log', params)

        model = Model(config=self.config,
                      token=ctx['token'],
                      username=ctx['user_id'])

        result = model.get_job_log(
            params['job_id'],
            search=params.get('search', None),
            level=params.get('level', None),
            offset=params.get('offset', 0),
            limit=params.get('limit', 10))

        self.validation.validate_result('get_job_log', result)
        #END get_job_log

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method get_job_log return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def cancel_job(self, ctx, params):
        """
        :param params: instance of type "CancelJobParams" (********* *
           cancel_job *********) -> structure: parameter "job_id" of type
           "JobID" (Core types)
        :returns: instance of type "CancelJobResult" -> structure: parameter
           "canceled" of type "bool" (Type synonym conveniences)
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN cancel_job
        self.validation.validate_params('cancel_job', params)

        model = Model(config=self.config,
                      token=ctx['token'],
                      username=ctx['user_id'])

        canceled = model.cancel_job(params['job_id'])

        result = {
            'canceled': canceled
        }

        self.validation.validate_result('cancel_job', result)
        #END cancel_job

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method cancel_job return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def get_job_types(self, ctx):
        """
        :returns: instance of type "GetJobTypesResult" (********* *
           get_job_types *********) -> structure: parameter
           "job_type_definitions" of list of type "DomainDefinition" ->
           structure: parameter "code" of String, parameter "description" of
           String, parameter "notes" of String
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN get_job_types
        # No params to validate!
        d = self.definitions.get('job_types')
        result = {'job_types': d}
        self.validation.validate_result('get_job_types', result)
        #END get_job_types

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method get_job_types return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def get_job_states(self, ctx):
        """
        :returns: instance of type "GetJobStatesResult" (********* *
           get_job_states *********) -> structure: parameter "job_states" of
           list of type "DomainDefinition" -> structure: parameter "code" of
           String, parameter "description" of String, parameter "notes" of
           String
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN get_job_states
        d = self.definitions.get('job_states')
        result = {'job_states': d}
        self.validation.validate_result('get_job_states', result)
        #END get_job_states

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method get_job_states return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def get_client_groups(self, ctx):
        """
        :returns: instance of type "GetClientGroupsResult" (********* *
           get_client_groups *********) -> structure: parameter
           "searchable_job_fields" of list of type "DomainDefinition" ->
           structure: parameter "code" of String, parameter "description" of
           String, parameter "notes" of String
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN get_client_groups
        d = self.definitions.get('client_groups')
        result = {'client_groups': d}
        self.validation.validate_result('get_client_groups', result)
        #END get_client_groups

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method get_client_groups return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def get_searchable_job_fields(self, ctx):
        """
        :returns: instance of type "GetSearchableJobFieldsResult" (*********
           * get_searchable_job_fields *********) -> structure: parameter
           "searchable_job_fields" of list of type "DomainDefinition" ->
           structure: parameter "code" of String, parameter "description" of
           String, parameter "notes" of String
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN get_searchable_job_fields
        d = self.definitions.get('searchable_job_fields')
        result = {'searchable_job_fields': d}
        self.validation.validate_result('get_searchable_job_fields', result)
        #END get_searchable_job_fields

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method get_searchable_job_fields return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def get_sort_specs(self, ctx):
        """
        :returns: instance of type "GetSortSpecsResult" -> structure:
           parameter "sort_fields" of list of type "SortSpecDefinition"
           (********* * get_sort_keys *********) -> structure: parameter
           "key" of String, parameter "fields" of list of String, parameter
           "description" of String
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN get_sort_specs
        d = self.definitions.get('sort_specs')
        result = {'sort_specs': d}
        self.validation.validate_result('get_sort_specs', result)
        #END get_sort_specs

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method get_sort_specs return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def get_log_levels(self, ctx):
        """
        :returns: instance of type "GetLogLevelsResult" (********* *
           get_log_levels *********) -> structure: parameter "log_levels" of
           list of type "OrderedDomainDefinition" -> structure: parameter
           "code" of String, parameter "order" of Long, parameter
           "description" of String, parameter "notes" of String
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN get_log_levels
        d = self.definitions.get('log_levels')
        result = {'log_levels': d}
        self.validation.validate_result('get_log_levels', result)
        #END get_log_levels

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method get_log_levels return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def is_admin(self, ctx):
        """
        :returns: instance of type "IsAdminResult" (********* * is_admin
           *********) -> structure: parameter "is_admin" of type "bool" (Type
           synonym conveniences)
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN is_admin
        model = Model(config=self.config,
                      token=ctx['token'],
                      username=ctx['user_id'])

        is_admin = model.is_metrics_admin()
        result = {'is_admin': is_admin}
        self.validation.validate_result('is_admin', result)
        #END is_admin

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method is_admin return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
