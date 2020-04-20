# -*- coding: utf-8 -*-
# BEGIN_HEADER
import logging
from JobBrowserBFF.Validation import Validation
from JobBrowserBFF.model.Model import Model
from JobBrowserBFF.definitions.Definitions import Definitions
# END_HEADER


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
    GIT_COMMIT_HASH = "e2f696d69a9957e3a396baea38b3a22b0d64d72d"

    # BEGIN_CLASS_HEADER
    # END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        # BEGIN_CONSTRUCTOR
        self.validation = Validation(schema_dir="impl", load_schemas=True)

        # fix up the config because, as an INI file, everything is a string...
        config['default-timeout'] = int(config['default-timeout'])

        self.validation.validate_config(config)
        self.config = config

        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)

        self.definitions = Definitions(load=True)
        # END_CONSTRUCTOR
        pass

    def get_jobs(self, ctx, params):
        """
        :param params: instance of type "GetJobsParams" (get_jobs Given a set
           of job ids, returns the job information for each job, in the same
           order as the ids were provided. As with other methods, this one
           takes an "admin" parameter which indicates whether the call is
           intended for administrator usage or not. If for administrator
           usage, the token provided in the call must be associated with an
           account with admin privileges for the upstream service. An error
           with code 50 is returned otherwise. Params: - job_ids: a list of
           job ids to look up and provide information about - admin: a
           boolean indicating whether the request is for a admin usage or not
           Returns: - jobs - list of JobStatus Throws: - 10 - Job not found:
           If the any of the given job ids are not found) -> structure:
           parameter "job_ids" of list of type "JobID" (Core types),
           parameter "admin" of type "bool" (Type synonym conveniences)
        :returns: instance of type "GetJobsResult" -> structure: parameter
           "jobs" of list of type "JobInfo" -> structure: parameter "job_id"
           of type "JobID" (Core types), parameter "owner" of type "User" ->
           structure: parameter "UserID" of String, parameter "realname" of
           String, parameter "state" of type "JobState" (Superset of all
           fields used to represent job state See the TS typing and
           json-schema) -> structure: parameter "status" of type "JobStatus"
           (create | queue | run | complete | error | terminate), parameter
           "create_at" of type "epoch_time", parameter "queue_at" of type
           "epoch_time", parameter "run_at" of type "epoch_time", parameter
           "finish_at" of type "epoch_time", parameter "client_group" of type
           "ClientGroup" (njs, bigmem, bigmemlong, kb_import, ...), parameter
           "error" of type "JobError" -> structure: parameter "code" of type
           "JobErrorCode", parameter "message" of String, parameter
           "service_error" of type "JSONRPC11Error" -> structure: parameter
           "code" of Long, parameter "message" of String, parameter "error"
           of unspecified object, parameter "termination" of type
           "JobTermination" -> structure: parameter "code" of type
           "JobTerminationCode", parameter "message" of String, parameter
           "app" of type "AppInfo" -> structure: parameter "module_name" of
           String, parameter "function_name" of String, parameter "title" of
           String, parameter "client_groups" of list of String, parameter
           "context" of type "JobContext" -> structure: parameter "type" of
           type "JobContextType" (narrative, export, workspace, unknown),
           parameter "workspace" of type "WorkspaceInfo" (represents the
           context in which the job was spawned. should collapse to
           narrative, perhaps, when all is said and done, but at the moment
           there are: narrative, export, workspace, unknown) -> structure:
           parameter "id" of Long, parameter "is_accessible" of type "bool"
           (Type synonym conveniences), parameter "name" of String, parameter
           "is_deleted" of type "bool" (Type synonym conveniences), parameter
           "narrative" of type "NarrativeInfo" -> structure: parameter
           "title" of String, parameter "is_temporary" of type "bool" (Type
           synonym conveniences)
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN get_jobs
        self.validation.validate_params('get_jobs', params)

        model = Model(config=self.config, context=ctx, timeout=params['timeout']).get_model(ctx)

        jobs = model.get_jobs(params)

        result = {
            'jobs': jobs
        }

        self.validation.validate_result('get_jobs', result)
        # END get_jobs

        return [result]

    def query_jobs(self, ctx, params):
        """
        :param params: instance of type "QueryJobsParams" (TODO: expand to
           match the filtering, sorting, searching of kb_metrics) ->
           structure: parameter "jobs" of list of type "JobID" (Core types),
           parameter "sort" of list of type "SortSpec" -> structure:
           parameter "key" of type "SortKey" (behaves as an enum: narrative,
           app, submitted, status), parameter "direction" of type
           "SortDirection" (behaves as an enum: ascending, descending),
           parameter "search" of type "SearchSpec" -> structure: parameter
           "terms" of list of String, parameter "filter" of type "FilterSpec"
           -> structure: parameter "workspace_id" of list of Long, parameter
           "status" of list of String, parameter "username" of list of
           String, parameter "app_id" of list of String, parameter "job_id"
           of list of String, parameter "error_code" of list of Long,
           parameter "terminated_code" of list of Long, parameter "time_span"
           of type "TimeSpanSpec" -> structure: parameter "from" of type
           "epoch_time", parameter "to" of type "epoch_time", parameter
           "client_groups" of list of type "ClientGroup" (njs, bigmem,
           bigmemlong, kb_import, ...), parameter "offset" of Long, parameter
           "limit" of Long, parameter "admin" of type "bool" (Type synonym
           conveniences)
        :returns: instance of type "QueryJobsResult" -> structure: parameter
           "jobs" of list of type "JobInfo" -> structure: parameter "job_id"
           of type "JobID" (Core types), parameter "owner" of type "User" ->
           structure: parameter "UserID" of String, parameter "realname" of
           String, parameter "state" of type "JobState" (Superset of all
           fields used to represent job state See the TS typing and
           json-schema) -> structure: parameter "status" of type "JobStatus"
           (create | queue | run | complete | error | terminate), parameter
           "create_at" of type "epoch_time", parameter "queue_at" of type
           "epoch_time", parameter "run_at" of type "epoch_time", parameter
           "finish_at" of type "epoch_time", parameter "client_group" of type
           "ClientGroup" (njs, bigmem, bigmemlong, kb_import, ...), parameter
           "error" of type "JobError" -> structure: parameter "code" of type
           "JobErrorCode", parameter "message" of String, parameter
           "service_error" of type "JSONRPC11Error" -> structure: parameter
           "code" of Long, parameter "message" of String, parameter "error"
           of unspecified object, parameter "termination" of type
           "JobTermination" -> structure: parameter "code" of type
           "JobTerminationCode", parameter "message" of String, parameter
           "app" of type "AppInfo" -> structure: parameter "module_name" of
           String, parameter "function_name" of String, parameter "title" of
           String, parameter "client_groups" of list of String, parameter
           "context" of type "JobContext" -> structure: parameter "type" of
           type "JobContextType" (narrative, export, workspace, unknown),
           parameter "workspace" of type "WorkspaceInfo" (represents the
           context in which the job was spawned. should collapse to
           narrative, perhaps, when all is said and done, but at the moment
           there are: narrative, export, workspace, unknown) -> structure:
           parameter "id" of Long, parameter "is_accessible" of type "bool"
           (Type synonym conveniences), parameter "name" of String, parameter
           "is_deleted" of type "bool" (Type synonym conveniences), parameter
           "narrative" of type "NarrativeInfo" -> structure: parameter
           "title" of String, parameter "is_temporary" of type "bool" (Type
           synonym conveniences), parameter "found_count" of Long, parameter
           "total_count" of Long
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN query_jobs
        self.validation.validate_params('query_jobs', params)

        model = Model(self.config, ctx).get_model(ctx)
        jobs, found_count, total_count = model.query_jobs(params)

        result = {
            'jobs': jobs,
            'found_count': found_count,
            'total_count': total_count
        }

        self.validation.validate_result('query_jobs', result)
        # END query_jobs

        return [result]

    def get_job_log(self, ctx, params):
        """
        :param params: instance of type "GetJobLogParams" -> structure:
           parameter "job_id" of type "JobID" (Core types), parameter
           "search" of type "SearchSpec" -> structure: parameter "terms" of
           list of String, parameter "level" of list of type "LogLevel"
           (enum-like: default, error), parameter "offset" of Long, parameter
           "limit" of Long, parameter "admin" of type "bool" (Type synonym
           conveniences)
        :returns: instance of type "GetJobLogResult" -> structure: parameter
           "log" of list of type "LogEntry" -> structure: parameter
           "entry_number" of Long, parameter "created" of Long, parameter
           "entry" of String, parameter "level" of type "LogLevel"
           (enum-like: default, error), parameter "total_count" of Long
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN get_job_log
        self.validation.validate_params('get_job_log', params)

        model = Model(config=self.config, context=ctx, timeout=params['timeout']).get_model(ctx)

        result = model.get_job_log(params)

        self.validation.validate_result('get_job_log', result)
        # END get_job_log

        return [result]

    def cancel_job(self, ctx, params):
        """
        :param params: instance of type "CancelJobParams" (cancel_job Given a
           job id, attempt to cancel the associated job. Params: - job_id:
           The id for the job to cancel Returns: - nothing. Throws: - 10 -
           Job not found: If the given job id was not found Note that
           attempting to cancel a job which is not cancelable will not throw
           an error. This behavior may change in the future. At present one
           upstream service (njsw) ignores this condition, but another (ee2)
           returns an error. For ee2 that error is ignored.) -> structure:
           parameter "job_id" of type "JobID" (Core types), parameter "admin"
           of type "bool" (Type synonym conveniences), parameter "timeout" of
           Long
        :returns: instance of type "CancelJobResult" -> structure: parameter
           "canceled" of type "bool" (Type synonym conveniences)
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN cancel_job
        self.validation.validate_params('cancel_job', params)

        model = Model(config=self.config, context=ctx, timeout=params['timeout']).get_model(ctx)

        # Note no return value; or rather a bare null to emulate void.
        result = model.cancel_job(params)

        self.validation.validate_result('cancel_job', result)
        # END cancel_job

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
        # BEGIN get_job_types
        # No params to validate!
        d = self.definitions.get('job_types')
        result = {'job_types': d}
        self.validation.validate_result('get_job_types', result)
        # END get_job_types

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
        # BEGIN get_job_states
        d = self.definitions.get('job_states')
        result = {'job_states': d}
        self.validation.validate_result('get_job_states', result)
        # END get_job_states

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
        # BEGIN get_client_groups
        d = self.definitions.get('client_groups')
        result = {'client_groups': d}
        self.validation.validate_result('get_client_groups', result)
        # END get_client_groups

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
        # BEGIN get_searchable_job_fields
        d = self.definitions.get('searchable_job_fields')
        result = {'searchable_job_fields': d}
        self.validation.validate_result('get_searchable_job_fields', result)
        # END get_searchable_job_fields

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
        # BEGIN get_sort_specs
        d = self.definitions.get('sort_specs')
        result = {'sort_specs': d}
        self.validation.validate_result('get_sort_specs', result)
        # END get_sort_specs

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
        # BEGIN get_log_levels
        d = self.definitions.get('log_levels')
        result = {'log_levels': d}
        self.validation.validate_result('get_log_levels', result)
        # END get_log_levels

        return [result]

    def is_admin(self, ctx):
        """
        :returns: instance of type "IsAdminResult" (********* * is_admin
           *********) -> structure: parameter "is_admin" of type "bool" (Type
           synonym conveniences)
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN is_admin
        model = Model(self.config, ctx).get_model(ctx)

        is_admin = model.is_admin()
        result = {'is_admin': is_admin}
        self.validation.validate_result('is_admin', result)
        # END is_admin

        return [result]

    def status(self, ctx):
        # BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        # END_STATUS
        return [returnVal]
